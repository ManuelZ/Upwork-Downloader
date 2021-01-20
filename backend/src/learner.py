# Built-in imports
from datetime import timedelta
from datetime import datetime
import sqlite3 as sql
from pathlib import Path
from time import time
import pickle
from io import BytesIO
import base64
from collections import defaultdict
from itertools import cycle

# External imports
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import category_encoders as ce
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
#from sklearn.pipeline import Pipeline
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score, precision_score, f1_score
from sklearn.metrics import make_scorer
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve

# Local imports
from src.config import TIMESTAMP_FORMAT
from src.utils import load_database_data
from src.utils import load_unlabeled_data
from src.utils import gen_parameters_from_log_space
from src.utils import identity
from src.config import MODEL_FILENAME
from src.config import LABELS
from src.preprocessors import SpacyPreprocessor
from src.preprocessors import SpacyVectorizer
from src.preprocessors import Quantizer

pd.set_option('display.max_columns', 5000)
pd.set_option('display.max_colwidth', 5000)


def load_model():
    print("Loading model...")
    model  = pickle.load(open(MODEL_FILENAME, 'rb'))
    le     = pickle.load(open('label_encoder.pkl', 'rb'))
    report = pickle.load(open('report.pkl', 'rb'))
    print("Model loaded.")

    return model,le,report


def train_model(classifier='SVC', search=False, scorer_name='precision'):
    """


    Args:
        classifier  : name of the classifier to use
        search      : bool to denote if hyperparameter search should be done
        scorer_name : name of the scorer to use

    Returns
        - confusion matrix
        - confusion matrix image
        - list of wrongly classified jobs
    """

    if scorer_name == 'precision':
        scorer = make_scorer(
            score_func = precision_score,
            average    = "macro" 
        )

    elif scorer_name == 'recall':
        scorer = make_scorer(
            score_func = recall_score,
            average    = "macro" 
        )

    elif scorer_name == 'f1':
        scorer = make_scorer(
            score_func = f1_score,
            average    = "macro" 
        )

    df = load_database_data(LABELS)

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
    
    model = train_with_bag_of_words(
        X_train    = X_train,
        y_train    = y_train,
        scorer     = scorer,
        classifier = classifier,
        search     = search
    )

    # model = train_bag_of_quantized_word_embeddings(
    #     X_train, y_train, scorer, search=search
    # )

    print("Creating performance report...")
    results = training_results(
        [model], X_train, y_train, X_test, y_test, le, scorer, scorer_name
    )

    print("Saving model and report...")
    pickle.dump(model, open(MODEL_FILENAME, 'wb'))
    pickle.dump(le, open('label_encoder.pkl', 'wb'))
    pickle.dump(results, open('results.pkl', 'wb'))
    print("Model and report saved.")

    return results


def predict_unlabeled_jobs(
    n_jobs      = 10,
    window_days = 2,
    to_predict  = { 'Good': True, 'Maybe': True, 'Bad': False, 'Irrelevant': False },
    ):
    """
    Args:
        n_jobs      : Number of jobs to return
        window_days : How many days to look back for unlabeled jobs
    """

    start = time()

    unlabeled = load_unlabeled_data()

    if not (
        Path(MODEL_FILENAME).exists() and 
        Path('label_encoder.pkl').exists() and 
        Path('report.pkl').exists()
    ):
        
        train_model()
    
    model, le, report = load_model()

    now = datetime.now(tz=pytz.timezone('America/Lima'))
    window = timedelta(days=window_days)
    unlabeled = unlabeled.loc[unlabeled['date_created'] >= now - window, :]

    if unlabeled.shape[0] == 0:
        print("Zero results, returning void results.")
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
    

    model_name = str(model.named_steps['classifier'].__class__)

    if 'SVC' in model_name:
        # distance to hyperplanes
        score = np.array(model.decision_function(unlabeled)) 
    
    elif 'LogisticRegression' in model_name:
        score = np.array(model.predict_proba(unlabeled)) * 100

    elif 'GradientBoostingClassifier' in model_name:
        score = np.array(model.predict_proba(unlabeled)) * 100

    elif 'VotingClassifier' in model_name:
        score = np.array(model.predict_proba(unlabeled)) * 100

    # Create new columns for the unlabeled jobs
    assignments = { c : score[:,i] for i,c in enumerate(le.classes_) }
    assignments['predicted'] = predicted_class
    assignments['score']     = score.max(axis=1)

    # Add columns with new information
    unlabeled = unlabeled.assign(**assignments)
    unlabeled.sort_values(by=['score'], inplace=True, ascending=False)

    unlabeled_good  = unlabeled.loc[unlabeled.predicted == 'Good', :].copy()
    unlabeled_maybe = unlabeled.loc[unlabeled.predicted == 'Maybe', :].copy()
    unlabeled_bad   = unlabeled.loc[unlabeled.predicted == 'Bad', :].copy()
    unlabeled_irrelevant = unlabeled.loc[unlabeled.predicted == 'Irrelevant', :].copy()

    selected_jobs = []
    n_collected = 0
    for type_df, subdf in [
        ('Good', unlabeled_good),
        ('Maybe',  unlabeled_maybe),
        ('Bad', unlabeled_bad),
        ('Irrelevant', unlabeled_irrelevant)
    ]:
        for i,row in subdf.iterrows():
            
            if n_collected == n_jobs:
                break

            if not (now < row['date_created'] + window):
                continue

            if (type_df == 'Good') and to_predict['Good']:
                selected_jobs.append(row)
                n_collected += 1

            elif (type_df == 'Maybe') and to_predict['Maybe']:
                selected_jobs.append(row)
                n_collected += 1
            
            elif (type_df == 'Bad') and to_predict['Bad']:
                selected_jobs.append(row)
                n_collected += 1

            elif (type_df == 'Irrelevant') and to_predict['Irrelevant']:
                selected_jobs.append(row)
                n_collected += 1

    end = time()
    print(f"Prediction took {end - start:.1f} seconds.")
    
    return selected_jobs, report


def train_with_bag_of_words(X_train, y_train, scorer, classifier='SVC', search=True):
    """
    Pass the data through a pipeline and return a trained model.

    Args:
        X_train: Train data
        y_train: Labels for the train data (transformed by LabelEncoder)
        search : Whether to search for the best hyperparameters
    """

    estimators = {
        'SVC' : SVC(
            C                       = 5.1,
            kernel                  = 'linear', 
            decision_function_shape = 'ovr',
            #class_weight            = 'balanced' # better without 'balanced'
        ),
        'LogisticRegression' : LogisticRegression(
            C           = 5.1,
        ),
        'GradientBoostingClassifier' : GradientBoostingClassifier(
            learning_rate=0.3
        ),
    }

    if classifier != 'VotingClassifier':
        clf = estimators.get(classifier)
    else:
        estimators['SVC'].probability = True
        clf = VotingClassifier(
            estimators = [(k,v) for k,v in estimators.items()],
            voting     = 'soft'
        )

    print(clf)

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

        #('oversampling', ADASYN(random_state=42)),

        ('classifier', clf),
    ], verbose=True)

    if search:

        log_space = gen_parameters_from_log_space(
            low_value  = 5,
            high_value = 8,
            n_samples  = 10
        )

        lin_space = np.arange(2, 8, 2, dtype=np.int)

        if classifier == 'SVC':
            grid = {
                # 'union__title_vec__tfidf__ngram_range'   : [(1,2), (2,2)],
                # 'union__snippet_vec__tfidf__ngram_range' : [(1,2), (2,2)],
                # 'union__snippet_vec__svd__n_components'  : np.arange(50, 301, 50),
                # 'union__title_vec__svd__n_components'    : np.arange(100, 301, 50),
                'classifier__C'                          : log_space,
            }
        
        elif classifier == 'LogisticRegression':
            grid = {
                'classifier__C': gen_parameters_from_log_space(0.1,10,10),
            }

        elif classifier == 'GradientBoostingClassifier':
            grid = {
                'classifier__learning_rate': gen_parameters_from_log_space(0.01,1,10),
            }
        
        elif classifier == 'VotingClassifier':
            grid = {
                'classifier__lr__C'         : gen_parameters_from_log_space(0.1,10,10),
                'classifier__C'             : gen_parameters_from_log_space(5,8,10),
                'classifier__learning_rate' : gen_parameters_from_log_space(0.01,1,10),
            }

        # With scoring="ovo", computes the average AUC of all possible pairwise 
        # combinations of classes. Insensitive to class imbalance when 
        # average='macro'.
        # Also see: https://stackoverflow.com/a/62471736/1253729

        searcher = GridSearchCV(
            estimator          = pipeline, 
            param_grid         = grid,
            n_jobs             = 4, 
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
                ('scaler', StandardScaler(), [
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

        ('classifier', SVC(
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


def training_results(
    models, X_train, y_train, X_test, y_test, le, scorer, scorer_name):
    """

    Args:
        y_test: Labels of the data (transformed by LabelEncoder)
    """

    # e.g. for results
    # 'SVC' : {
    #     'scores'         : { 
    #         'precision' : {
    #             'train': 0.9,
    #             'test' : 0.8
    #         }
    #     },
    #     'conf_matrix_im' : "base64..."
    #     'pr_rec_im'       : "base64..."
    # }
    results = {}

    for model in models:

        if 'GridSearchCV' in type(model).__name__:
            model_name = type(model.best_estimator_.named_steps['classifier']).__name__
        else:
            model_name = type(model.named_steps['classifier']).__name__


        if not model_name in results:
            results[model_name] = {}
            if not 'scores' in results[model_name]:
                results[model_name]['scores'] = {}
                if not scorer_name in results[model_name]['scores']:
                    results[model_name]['scores'][scorer_name] = {
                        'train' : None,
                        'test'  : None
                    }

        #######################################################################
        # Save scores
        #######################################################################

        train_score = scorer(model, X_train, y_train)
        test_score  = scorer(model, X_test, y_test)
        results[model_name]['scores'][scorer_name]['train'] = train_score
        results[model_name]['scores'][scorer_name]['test']  = test_score

        # Go back to the original str labels
        y_pred    = le.inverse_transform(model.predict(X_test))
        y_test_tr = le.inverse_transform(y_test)
        

        #######################################################################
        # Save Confusion Matrix on the test data
        #######################################################################

        report = classification_report(y_test_tr, y_pred, output_dict=True)
        report = pd.DataFrame(report).round(2).T

        disp = plot_confusion_matrix(
            estimator      = model,
            X              = X_test,
            y_true         = y_test,
            display_labels = le.classes_,
            cmap           = plt.cm.Blues,
            normalize      = 'true'
        )

        disp.ax_.set_title(
            f"{model_name} on test set - {scorer_name}:"
            f" {test_score:.2f}"
        )
        
        buffer = BytesIO()
        plt.savefig(buffer, format='jpg')
        conf_matrix_im = base64.encodebytes(buffer.getvalue()).decode('ascii')
        buffer.close()

        results[model_name]['conf_matrix_im'] = conf_matrix_im

        #######################################################################
        # Save Precision-Recall curve
        # From: 
        # https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html
        #######################################################################
        
        colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])
        
        n_classes     = len(LABELS) 
        precision     = {}
        recall        = {}
        avg_precision = {}

        if model_name == 'SVC':
            y_score = model.decision_function(X_test)
        else:
            y_score = model.predict_proba(X_test)

        lb = LabelBinarizer()
        y_test = lb.fit_transform(y_test)

        for i in le.transform(LABELS): 

            # Note:
            # Precision-Recall or ROC curves accept either probabilities or the 
            # output of a decision function.
            # More details: https://stats.stackexchange.com/a/178865/55820
            precision[i], recall[i], _ = precision_recall_curve(
                y_true      = y_test[:, i], 
                probas_pred = y_score[:, i] # Estimated probabilities 
            )                               # or output of a decision function
            
            avg_precision[i] = average_precision_score(
                y_test[:, i], y_score[:, i]
            )

        # A "micro-average": quantifying score on all classes jointly
        precision["micro"], recall["micro"], _ = precision_recall_curve(
            y_test.ravel(), y_score.ravel()
        )
        avg_precision["micro"] = average_precision_score(
            y_test, y_score, average="micro"
        )

        print(
            f'Average precision score, micro-averaged over all classes:'
            f'{avg_precision["micro"]:0.2f}'
        )

        plt.figure(figsize=(7, 8)) # width,height
        f_scores = np.linspace(0.2, 0.8, num=4)
        lines = []
        labels = []

        # Iso-f1 curves
        for f_score in f_scores:
            x = np.linspace(0.01, 1)
            y = f_score * x / (2 * x - f_score)
            l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
            plt.annotate(f'f1={f_score:0.1f}', xy=(0.9, y[45] + 0.02))

        # Label for iso-curves
        lines.append(l)
        labels.append('Iso-f1 curves')

        # Label for micro-average
        l, = plt.plot(recall["micro"], precision["micro"], color='gold', lw=2)
        lines.append(l)
        labels.append('micro-average Precision-recall (area = {0:0.2f})'
                      ''.format(avg_precision["micro"]))

        # Labels for classes
        for i,color in zip(le.transform(LABELS), colors):
            l, = plt.plot(recall[i], precision[i], color=color, lw=2)
            lines.append(l)
            label_name = le.inverse_transform([i])
            labels.append("Precision-recall for class '{0}' (area = {1:0.2f})"
                          "".format(label_name[0], avg_precision[i]))

        fig = plt.gcf()
        fig.subplots_adjust(bottom=0.25)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall curves for {model_name}')
        plt.legend(lines, labels, loc=(0, -0.4), prop=dict(size=10))

        buffer = BytesIO()
        plt.savefig(buffer, format='jpg')
        pr_rec_im = base64.encodebytes(buffer.getvalue()).decode('ascii')
        buffer.close()

        results[model_name]['pr_rec_im'] = pr_rec_im
    
    return results
