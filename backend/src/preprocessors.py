# Built-in imports
import string

# External imports
from sklearn.base import BaseEstimator, TransformerMixin
import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS


class SpacyPreprocessor(BaseEstimator, TransformerMixin):
    """
    For tokenization of text using:
    - lemmatization
    - stop words removal (this is also handled by tfidf)
    - 
    """
    def __init__(self):
        self.nlp       = English()
        self.tokenizer = self.nlp.Defaults.create_tokenizer(self.nlp)
        self.stopwords = STOP_WORDS

    def fit(self, X, y=None):
        """
        Fit simply returns self, no other information is needed.
        """
        return self

    def transform(self, X):
        """
        Actually runs the preprocessing on each document.
        """
        return [
            list(self.tokenize(doc)) for doc in X
        ]

    def tokenize(self, document):
        """
        Tokenize a document by lemmatization while removing stop words and 
        punctuation.
        """
        tokens = self.tokenizer(document)
        token_list = [tk.lemma_ for tk in tokens if not (tk.is_stop or tk.is_punct)]
        return token_list