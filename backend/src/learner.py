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
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score, precision_score
from sklearn.metrics import make_scorer

# Local imports
from src.config import TIMESTAMP_FORMAT
from src.preprocessors import SpacyPreprocessor
from src.utils import load_database_data
from src.config import MODEL_FILENAME

pd.set_option('display.max_colwidth', 1000)


def identity(arg):
    """ Simple identity function used in TfidfVEctorizer as passthrough"""
    return arg


def gen_parameters_from_log_space(low_value=0.0001, high_value=0.001, n_samples=5):
    """
    Generate a list of parameters by sampling uniformly from a logarithmic space
    
    E.g.
           [ x   x  x | x  x x   |  x  x x  | x  x   x ]
        0.0001      0.001       0.01       0.1         1
    
    Which will draw much more small numbers than larger ones.
    """
    a = np.log10(low_value)
    b = np.log10(high_value)
    r = np.sort(np.random.uniform(a, b, n_samples))
    return 10 ** r


def train(X_train, y_train, search=True):
    """
    Pass the data through a pipeline and return a trained model.

    Args:
        X_train: Train data
        y_train: Labels for the train data
        search : Whether to search for the best hyperparameters
    """

    classifier = svm.SVC(
        C                       = 1.4,
        kernel                  = 'linear', 
        decision_function_shape = 'ovr',
        class_weight            = 'balanced'
    )

    pipeline = Pipeline([
        # Use ColumnTransformer to combine the features from subject and body
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
                    ('preprocessor', SpacyPreprocessor()), # tokenization, stop-words, lemmatization
                    ('tfidf', TfidfVectorizer(
                        tokenizer    = identity,
                        preprocessor = None,
                        lowercase    = False,
                        use_idf      = True,
                        ngram_range  = (1,2)
                    )),
                    ('svd', TruncatedSVD(n_components=150)),
                ]), 'title'),

                ('snippet_vec', Pipeline([
                    ('preprocessor', SpacyPreprocessor()), # tokenization, stop-words, lemmatization
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

        ('classifier', classifier),
    ], verbose=True)

    if search:

        log_space = gen_parameters_from_log_space(
            low_value  = 0.5,
            high_value = 5,
            n_samples  = 10
        )

        grid = {
            # 'union__snippet_vec__svd__n_components' : np.arange(50, 301, 50),
            # 'union__title_vec__svd__n_components' : np.arange(100, 301, 50),
            # 'classifier__C' : log_space,
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

        # With scoring="ovo", computes the average AUC of all possible pairwise 
        # combinations of classes. Insensitive to class imbalance when 
        # average='macro'.
        # Also see: https://stackoverflow.com/a/62471736/1253729
        scorer = make_scorer(
            score_func  = precision_score,
            average     = "macro" 
        )

        searcher = GridSearchCV(
            estimator          = pipeline, 
            param_grid         = grid,
            n_jobs             = 7, 
            return_train_score = True, 
            refit              = True,
            verbose            = 1,
            cv                 = StratifiedKFold(n_splits=3),
            scoring            = scorer,
        )

        model = searcher.fit(X_train, y_train.values.ravel())

    else:
        model = pipeline.fit(X_train, y_train.values.ravel())
    
    print(f"Best found parameters: {searcher.best_params_}")

    return model


def training_report(model, X_train, y_train, X_test, y_test, le):
    """
    """

    train_score = model.score(X_train, y_train)
    print(f"Train score: {train_score:.2f}")
    
    test_score = model.score(X_test, y_test)
    print(f"Test score: {test_score:.2f}")

    y_pred = model.predict(X_test)
    y_pred = le.inverse_transform(y_pred)
    y_test = le.inverse_transform(y_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    report = pd.DataFrame(report).round(2).T

    return report


def predict_unlabeled_jobs(retrain=False, n_jobs=10, window_days=2):
    """
    Args:
        n_jobs      : Number of jobs to return
        window_days : How many days to look back for unlabeled jobs
    """
    start = time()
    
    df = load_database_data()

    # Encode the output labels
    le = LabelEncoder()
    le = le.fit(df.loc[:, 'label'].values.ravel())
    df.loc[:, 'label'] = le.transform(df.loc[:, 'label'].values.ravel())

    # TODO: load unlabeled data only if retrain=False
    X_train, X_test, y_train, y_test = load_data(df)

    unlabeled = load_unlabeled_data()

    if Path(MODEL_FILENAME).exists() and not retrain:
        print("Loading model...")
        model = pickle.load(open(MODEL_FILENAME, 'rb'))
        print("Model loaded.")
    else:

        # TODO: create the report here and save it, do not recreate it when 
        # loading data bacause it seems that the data used for the evaluation 
        # may be part of training
        model = train(X_train, y_train)
        print("Saving model...")
        pickle.dump(model, open(MODEL_FILENAME, 'wb'))
        print("Model saved.")
    
    print("Creating performance report...")
    report = training_report(model, X_train, y_train, X_test, y_test, le)
    print("Report created.")

    now = datetime.now(tz=pytz.timezone('America/Lima'))
    window = timedelta(days=window_days)
    
    # Filter by date some jobs
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
    # [2] https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC.decision_function
    # [3] https://www.econstor.eu/bitstream/10419/22569/1/tr56-04.pdf
    dist_to_hyperplanes = np.array(model.decision_function(unlabeled))
    pseudo_probs = np.exp(dist_to_hyperplanes) / np.sum(np.exp(dist_to_hyperplanes), axis=1).reshape(-1,1) # softmax after the voting

    # Weights assigned to the features (coefficients in the primal problem)
    # weights = model.best_estimator_.named_steps['classifier'].coef_
    
    print(f"Predicted class: {predicted_class}")
    print(f"Distances to hyperplanes: {dist_to_hyperplanes}")
    print(f"My pseudo-probability: {pseudo_probs}")
    
    assignments = {
        "predicted"    : predicted_class,
        "score"        : pseudo_probs.max(axis=1),
        le.classes_[0] : pseudo_probs[:,0], # e.g. "Good" or "Bad" or "Maybe"
        le.classes_[1] : pseudo_probs[:,1],
        le.classes_[2] : pseudo_probs[:,2]
    }

    # Add columns with new information
    unlabeled = unlabeled.assign(**assignments)
    unlabeled.sort_values(by=['score'], inplace=True, ascending=False)

    unlabeled_good  = unlabeled.loc[unlabeled.predicted == "Good", :].copy()
    unlabeled_maybe = unlabeled.loc[unlabeled.predicted == "Maybe", :].copy()
    unlabeled_bad   = unlabeled.loc[unlabeled.predicted == "Bad", :].copy()

    selected_jobs = []
    n_collected = 0
    for type_df, df in [("Good", unlabeled_good), ("Maybe",  unlabeled_maybe), ("Bad", unlabeled_bad)]:
        for i,row in df.iterrows():
            
            if n_collected == n_jobs:
                break

            if not (now < row['date_created'] + window):
                continue

            if type_df == "Good":
                selected_jobs.append(row)
                n_collected += 1

            elif type_df == "Maybe":
                selected_jobs.append(row)
                n_collected += 1
            
            elif type_df == "Bad":
                if row["score"] < 0.3:
                    selected_jobs.append(row)
                    n_collected += 1

    end = time()
    print(f"Prediction took {end - start:.1f} seconds.")
    return selected_jobs, report


def load_unlabeled_data():
    unlabeled = load_database_data(['Uncategorized'])
    unlabeled.date_created = pd.to_datetime(unlabeled.date_created)
    unlabeled.drop(['label'], axis=1, inplace=True)
    return unlabeled

def load_data(df, labeled=True):
    y = df.loc[:, 'label']
    X = df.drop(['label'], axis=1)

    X_train, X_test, y_train, y_test = \
        train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    print(f"Loaded {X_train.shape[0]} training examples and {X_test.shape[0]} validation examples.")
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    predict_unlabeled_jobs()
