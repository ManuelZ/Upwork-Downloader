# Built-in imports
from datetime import timedelta
from datetime import datetime
import sqlite3 as sql
import logging

# External imports
import pytz
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC
from sklearn.decomposition import TruncatedSVD

# Local imports
from src.config import TIMESTAMP_FORMAT
from src.preprocessors import NLTKPreprocessor
from src.preprocessors import StemmedCountVectorizer
from src.utils import load_database_data

pd.set_option('display.max_colwidth', 1000)


# stemmedVectorizer = StemmedCountVectorizer(lowercase=True,
#                                            stop_words='english',
#                                            analyzer='word',
#                                            # tokenizer=,
#                                            ngram_range=(2, 2),
#                                            )

def train(X_train, y_train):
    """

    """

    def identity(arg):
        """ Simple identity function works as a passthrough"""
        return arg

    pipeline = Pipeline([
        # Use ColumnTransformer to combine the features from subject and body
        ('union', ColumnTransformer(
            [
                # budget column
                ('budget', StandardScaler(), ['budget', 'client.feedback', 'client.reviews_count']),

                # title column
                ('title_vec', Pipeline([
                    ('preprocessor', NLTKPreprocessor()),
                    ('tfidf', TfidfVectorizer(tokenizer=identity, preprocessor=None, lowercase=False, use_idf=True)),
                ]), 'title'),

                # snippet column
                ('snippet_vec', Pipeline([
                    ('preprocessor', NLTKPreprocessor()),
                    ('tfidf', TfidfVectorizer(tokenizer=identity, preprocessor=None, lowercase=False, use_idf=True)),
                    ('best', TruncatedSVD(n_components=50)),
                ]), 'snippet'),
                
                # 
                ('ohe_cat', OneHotEncoder(), ["job_type"]),
            ], remainder='drop'
        )),

        # Classifier
        ('svc', LinearSVC(dual=False)),
    ], verbose=True)

    model = pipeline.fit(X_train, y_train.values.ravel())
    
    return model


def training_report(model, X_test, y_test):
    """
    """
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    report = pd.DataFrame(report).round(2).T
    return report


def predict_unlabeled_jobs(n_jobs=10, window_days=2):
    """
    Args:
        n_jobs      : Number of jobs to return
        window_days : How many days to look back for unlabeled jobs
    """

    X_train, X_test, y_train, y_test = load_data()

    unlabeled = load_unlabeled_data()

    model = train(X_train, y_train)
    report = training_report(model, X_test, y_test)
    print(report)

    now = datetime.now(tz=pytz.timezone('America/Lima'))
    window = timedelta(days=window_days)
    
    # Filter by date some jobs
    unlabeled = unlabeled.loc[unlabeled['date_created'] >= now - window, :]

    print(unlabeled)
    if unlabeled.shape[0] == 0:
        return []
    
    # Predict a class
    predicted_class = model.predict(unlabeled)

    # Calculate SVM probabilities
    # https://stackoverflow.com/questions/49507066/predict-probabilities-using-svm
    p = np.array(model.decision_function(unlabeled)) # decision is a voting function
    probs = np.exp(p) / np.sum(np.exp(p), axis=1).reshape(-1,1) # softmax after the voting
    
    # Add columns with new information
    unlabeled = unlabeled.assign(predicted=predicted_class, probability=probs.max(axis=1))
    unlabeled.sort_values(by=['probability'], inplace=True, ascending=False)

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
                if row["probability"] < 0.3:
                    selected_jobs.append(row)
                    n_collected += 1
            
            elif type_df == "Bad":
                if row["probability"] < 0.3:
                    selected_jobs.append(row)
                    n_collected += 1

    return selected_jobs


def load_unlabeled_data():
    unlabeled = load_database_data(['Uncategorized'])
    unlabeled.date_created = pd.to_datetime(unlabeled.date_created)
    unlabeled.drop(['label'], axis=1, inplace=True)
    return unlabeled

def load_data(labeled=True):
    df = load_database_data()
    y = df.loc[:, 'label']
    X = df.drop(['label'], axis=1)

    X_train, X_test, y_train, y_test = \
        train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    print(f"{X_train.shape[0]} training examples and {X_test.shape[0]} validation examples.")
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    predict_unlabeled_jobs()
