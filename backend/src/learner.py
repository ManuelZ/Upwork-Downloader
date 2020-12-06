# Built-in imports
from datetime import timedelta
from datetime import datetime
import sqlite3 as sql
from pathlib import Path
from time import time
import pickle

# External imports
import pytz
import pandas as pd
import numpy as np
from sklearn import svm
import category_encoders as ce
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score, precision_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split

# Local imports
from src.config import TIMESTAMP_FORMAT
from src.utils import load_database_data
from src.utils import load_unlabeled_data
from src.utils import gen_parameters_from_log_space
from src.utils import identity
from src.config import MODEL_FILENAME
from src.preprocessors import SpacyPreprocessor
from src.preprocessors import SpacyVectorizer
from src.preprocessors import Quantizer

pd.set_option('display.max_columns', 5000)
pd.set_option('display.max_colwidth', 5000)


def predict_unlabeled_jobs(
    retrain     = False,
    n_jobs      = 10,
    window_days = 2,
    to_predict  = { 'Good': True, 'Maybe': True, 'Bad': False },
    search      = False
    ):
    """
    Args:
        n_jobs      : Number of jobs to return
        window_days : How many days to look back for unlabeled jobs
    """

    start = time()

    unlabeled = load_unlabeled_data()

    if not retrain and (
            Path(MODEL_FILENAME).exists() and 
            Path('label_encoder.pkl').exists() and 
            Path('report.pkl').exists()
        ):

        print("Loading model...")
        model  = pickle.load(open(MODEL_FILENAME, 'rb'))
        le     = pickle.load(open('label_encoder.pkl', 'rb'))
        report = pickle.load(open('report.pkl', 'rb'))
        print("Model loaded.")

    else:
        scorer = make_scorer(
            score_func = precision_score,
            average    = "macro" 
        )

        df = load_database_data(['Good', 'Bad', 'Maybe'])

        # Encode the output labels
        le = LabelEncoder()
        df.loc[:,'label'] = le.fit_transform(df.loc[:,'label'].values.ravel())

        y = df.loc[:, 'label'].copy()
        X = df.drop(['label'], axis=1).copy()

        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        
        print(
            f"Loaded {X_train.shape[0]} training examples and "
            f"{X_test.shape[0]} validation examples."
        )

        # TODO: pass search as a parameter directly from the UI
        
        model = train_with_bag_of_words(
            X_train, y_train, scorer, search=search
        )

        # model = train_bag_of_quantized_word_embeddings(
        #     X_train, y_train, scorer, search=search
        # )

        print("Creating performance report...")
        report = training_report(
            model, X_train, y_train, X_test, y_test, le, scorer
        )

        print(report)

        print("Saving model and report...")
        pickle.dump(model, open(MODEL_FILENAME, 'wb'))
        pickle.dump(le, open('label_encoder.pkl', 'wb'))
        pickle.dump(report, open('report.pkl', 'wb'))
        print("Model and report saved.")
    

    now = datetime.now(tz=pytz.timezone('America/Lima'))
    window = timedelta(days=window_days)
    unlabeled = unlabeled.loc[unlabeled['date_created'] >= now - window, :]

    if unlabeled.shape[0] == 0:
        return []
    
    # Predict a class
    predicted_class = model.predict(unlabeled)
    predicted_class = le.inverse_transform(predicted_class)

    # Calculate SVM probabilities?
    #
    # After researching, it looks like there is no simple way of obtaining 
    # probabilities out of SVM because it's not a probabilistic model, as 
    # mentioned in [1], which is a post linked by the documentation of 
    # `decision_function` in [2].
    # Similarly, in [3, p.4] is said that the mapping from decision functions 
    # to probabilities via softmax "is not very well founded, as the scaled 
    # values are not justified fro the data".
    # 
    # The following comes from the documentation:
    # The decision_function method of SVC gives per-class scores for each 
    # sample.
    # - If decision_function_shape=’ovo’, the function values are proportional 
    #   to the distance of the samples X to the separating hyperplane. If the 
    #   exact distances are required, divide the function values by the norm of
    #   the weight vector (coef_). 
    # - If decision_function_shape=’ovr’, the decision function is a monotonic 
    #   transformation of ovo decision function.
    #
    # [1] https://stats.stackexchange.com/a/14881/55820
    # [2] https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
    # [3] https://www.econstor.eu/bitstream/10419/22569/1/tr56-04.pdf
    
    score = np.array(model.decision_function(unlabeled)) # distance to hyperplanes
  
    assignments = {
        "predicted"    : predicted_class,
        "score"        : score.max(axis=1),
        le.classes_[0] : score[:,0], # e.g. "Good" or "Bad" or "Maybe"
        le.classes_[1] : score[:,1],
        le.classes_[2] : score[:,2]
    }

    # Add columns with new information
    unlabeled = unlabeled.assign(**assignments)
    unlabeled.sort_values(by=['score'], inplace=True, ascending=False)

    unlabeled_good  = unlabeled.loc[unlabeled.predicted == "Good", :].copy()
    unlabeled_maybe = unlabeled.loc[unlabeled.predicted == "Maybe", :].copy()
    unlabeled_bad   = unlabeled.loc[unlabeled.predicted == "Bad", :].copy()

    selected_jobs = []
    n_collected = 0
    for type_df, subdf in [
        ("Good", unlabeled_good),
        ("Maybe",  unlabeled_maybe),
        ("Bad", unlabeled_bad)
    ]:
        for i,row in subdf.iterrows():
            
            if n_collected == n_jobs:
                break

            if not (now < row['date_created'] + window):
                continue

            if (type_df == "Good") and to_predict['Good']:
                selected_jobs.append(row)
                n_collected += 1

            elif (type_df == "Maybe") and to_predict['Maybe']:
                selected_jobs.append(row)
                n_collected += 1
            
            elif (type_df == "Bad") and to_predict['Bad']:
                selected_jobs.append(row)
                n_collected += 1

    end = time()
    print(f"Prediction took {end - start:.1f} seconds.")
    
    return selected_jobs, report


def train_with_bag_of_words(X_train, y_train, scorer, search=True):
    """
    Pass the data through a pipeline and return a trained model.

    Args:
        X_train: Train data
        y_train: Labels for the train data
        search : Whether to search for the best hyperparameters
    """

    pipeline = Pipeline([
        ('union', ColumnTransformer(
            [
                ('scaler', StandardScaler(), [
                    'budget',
                    'client.feedback',
                    'client.reviews_count',
                    'client.jobs_posted',
                    'client.past_hires'
                ]),

                ('title_vec', Pipeline([
                    ('preprocessor', SpacyPreprocessor()),
                    ('tfidf', TfidfVectorizer(
                        tokenizer    = identity,
                        preprocessor = None,
                        lowercase    = False,
                        use_idf      = True,
                        ngram_range  = (2,2)
                    )),
                    ('svd', TruncatedSVD(n_components=150)),
                ]), 'title'),

                ('snippet_vec', Pipeline([
                    ('preprocessor', SpacyPreprocessor()),
                    ('tfidf', TfidfVectorizer(
                        tokenizer    = identity,
                        preprocessor = None,
                        lowercase    = False,
                        use_idf      = True,
                        sublinear_tf = False, # not good results when True
                        ngram_range  = (1,2)
                    )),
                    ('svd', TruncatedSVD(n_components=100)),
                ]), 'snippet'),
                
                ('cat', ce.CatBoostEncoder(), [
                    "job_type",
                    'category2',
                    'client.country'
                ]),
            ], remainder='drop'
        )),

        ('classifier', svm.SVC(
            C                       = 7.5,
            kernel                  = 'linear', 
            decision_function_shape = 'ovr',
            class_weight            = 'balanced'
        )),
    ], verbose=True)

    if search:

        log_space = gen_parameters_from_log_space(
            low_value  = 1,
            high_value = 20,
            n_samples  = 10
        )

        lin_space = np.arange(2, 10, 2, dtype=np.int)

        grid = {
            'union__title_vec__tfidf__ngram_range'   : [(1,2), (2,2)],
            'union__snippet_vec__tfidf__ngram_range' : [(1,2), (2,2)],
            'union__snippet_vec__svd__n_components'  : np.arange(50, 301, 50),
            'union__title_vec__svd__n_components'    : np.arange(100, 301, 50),
            'classifier__C'                          : lin_space,
        }

        # With scoring="ovo", computes the average AUC of all possible pairwise 
        # combinations of classes. Insensitive to class imbalance when 
        # average='macro'.
        # Also see: https://stackoverflow.com/a/62471736/1253729

        searcher = GridSearchCV(
            estimator          = pipeline, 
            param_grid         = grid,
            n_jobs             = 7, 
            return_train_score = True, 
            refit              = True,
            verbose            = True,
            cv                 = StratifiedKFold(n_splits=3),
            scoring            = scorer,
        )

        model = searcher.fit(X_train, y_train.values.ravel())
        print(f"Best found parameters: {searcher.best_params_}")

    else:
        model = pipeline.fit(X_train, y_train.values.ravel())

    return model


def train_bag_of_quantized_word_embeddings(
    X_train, y_train, scorer, search=False):

    """
    """
    print(f"Running train_bag_of_quantized_word_embeddings")

    pipeline = Pipeline([
        # Use ColumnTransformer to combine the features from subject and body
        ('union', ColumnTransformer(
            [
                ('scaler', MinMaxScaler(), [
                    'budget',
                    'client.feedback',
                    'client.reviews_count',
                    'client.jobs_posted',
                    'client.past_hires'
                ]),

                ('title_vec', Pipeline([
                    ('vectorize', SpacyVectorizer()),
                    ('quantize',  Quantizer(
                        n_clusters = 3000,
                        batch_size = 5000,
                        n_passes   = 1,
                    )),
                    ('tfidf',     TfidfTransformer()),
                    # ('svd',     TruncatedSVD(n_components=300)),
                ]), 'title'),

                ('snippet_vec', Pipeline([
                    ('vectorize', SpacyVectorizer()),
                    ('quantize',  Quantizer(
                        n_clusters = 4000,
                        batch_size = 10000,
                        n_passes   = 2,
                    )),
                    ('tfidf',     TfidfTransformer()),
                    # ('svd',     TruncatedSVD(n_components=300)),
                ]), 'snippet'),
                
                ('cat', ce.CatBoostEncoder(), [
                    "job_type",
                    'category2',
                    'client.country'
                ]),
            ], remainder='drop'
        )),

        ('classifier', svm.SVC(
            C                       = 9.2,
            kernel                  = 'linear', 
            decision_function_shape = 'ovr',
            class_weight            = 'balanced')),
    ], verbose=True)
    
    if search:
        print(f"Starting hyper-parameters search...")

        log_space = gen_parameters_from_log_space(
            low_value  = 22,
            high_value = 30,
            n_samples  = 5
        )

        grid = {
            # 'union__snippet_vec__quantize__n_clusters' : [3000, 5000, 10000],
            # 'union__title_vec__quantize__n_clusters'   : [1000, 2000, 3000],
            'classifier__C' : log_space,
            # 'classifier__kernel': [
            #     'linear',
            #     'poly',
            #     'rbf',
            #     'sigmoid'
            # ],
            
            # 'classifier__decision_function_shape' : [
            #     'ovo',
            #     'ovr'
            # ]
        }

        searcher = GridSearchCV(
            estimator          = pipeline, 
            param_grid         = grid,
            n_jobs             = 2, 
            return_train_score = True, 
            refit              = True,
            cv                 = StratifiedKFold(n_splits=3),
            scoring            = scorer,
            verbose            = 1,
        )

        model = searcher.fit(X_train, y_train.values.ravel())
        print(f"Best found parameters: {searcher.best_params_}")
        print(pd.DataFrame(model.cv_results_))
    else:
        print(f"Training model WITHOUT hyper-parameters search.")
        model = pipeline.fit(X_train, y_train.values.ravel())
    
    return model


def training_report(model, X_train, y_train, X_test, y_test, le, scorer):
    """
    """
    
    train_score = scorer(model, X_train, y_train)
    print(f"Train score: {train_score:.2f}")

    test_score = scorer(model, X_test, y_test)
    print(f"Test score: {test_score:.2f}")


    y_pred = le.inverse_transform(model.predict(X_test))
    y_test = le.inverse_transform(y_test)
    
    report = classification_report(y_test, y_pred, output_dict=True)
    report = pd.DataFrame(report).round(2).T

    return report
