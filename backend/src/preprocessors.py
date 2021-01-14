# Built-in imports
import string
import random

# External imports
import numpy as np
import spacy
from spacy.lang.en import English
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm

# Local imports
from src.config import SILHOUETTE_SAMPLE_SIZE
from src.config import SILHOUETTE_N_SAMPLES
from src.config import SILHOUETTE_TOL
from src.config import MAX_FAILED_PASSES


# nlp= English()
nlp = spacy.load("en_core_web_sm", disable=['tagger', 'parser', 'ner'])

class SpacyPreprocessor(BaseEstimator, TransformerMixin):
    """
    For tokenization of text using:
    - lemmatization
    - stop words removal (this is also handled by tfidf)
    - 
    """

    def __init__(self):
        self.tokenizer = nlp.Defaults.create_tokenizer(nlp)

    def fit(self, X, y=None):
        """
        Fit simply returns self, no other information is needed.
        """
        return self

    def transform(self, X):
        """
        Actually runs the preprocessing on each document.
        """
        return [list(self.tokenize(doc)) for doc in X]

    def tokenize(self, document):
        """
        Tokenize a document by lemmatization while removing stop words and 
        punctuation.
        """
        tokens = self.tokenizer(document)
        token_list = [
            tk.lemma_ for tk in tokens if not (tk.is_stop or tk.is_punct)
        ]
        
        return token_list


class SpacyVectorizer(BaseEstimator, TransformerMixin):
    """
    """

    def fit(self, X, y=None):
        """
        Fit simply returns self, no other information is needed.
        """
        return self

    def transform(self, X):
        """
        Actually runs the vectorization of each document.
        """
        return [self.vectorize(doc) for doc in X]

    def vectorize(self, document):
        """
        Return an array of word embeddings for all the words in this document,
        only if there are embeddings available.

        Returns
            Array of size (n,300) where n is the number of words in a document
            that have an available word embedding.
        """

        words     = 0
        no_vector = 0
        vectors   = []
        
        for token in nlp(document):
            if token.has_vector and not (token.is_stop or token.is_punct):
                vectors.append(token.vector)
            else:
                no_vector += 1
            words += 1
        
        p = 1  - (no_vector / words)
        
        # print(f"{p:.1%} of this document had vectors. Total words: {words}.")

        if len(vectors) == 0:
            return np.zeros((0,300), dtype=np.float32)

        stacked_vectors = np.stack(vectors, axis=0)

        return stacked_vectors


class Quantizer(BaseEstimator, TransformerMixin):
    """
    Beware when defining a new estimator
    https://scikit-learn.org/stable/developers/develop.html#instantiation
    """
    
    def __init__(self, n_clusters=100, batch_size=2500, n_passes=2):
        self.n_clusters = n_clusters
        self.batch_size = batch_size
        self.n_passes   = n_passes

    def fit(self, X, y=None):
        """
        Args:
            X: list of arrays of size (n, 300) where n is the number of docs
        """
        self.kmeans = BatchedKMeans(
            n_clusters        = self.n_clusters,
            max_num_passes    = self.n_passes,
            batch_size        = self.batch_size
        )
        X = np.concatenate(X, axis=0)
        self.kmeans.fit(X)
        
        return self

    def transform(self, X):
        """
        Return one histogram for each document.

        Args:
            X: list of arrays of size (n, 300) where n is the number of docs

        Returns:
            array of shape (n, n_clusters) where n is the number of docs
        """
        
        clusters_histograms = np.zeros((len(X), self.n_clusters))
        for i, document_descriptors in enumerate(X):
            if document_descriptors.shape[0] == 0:
                continue
            clusters_idxs = self.kmeans.predict(document_descriptors)
            values, _ = np.histogram(clusters_idxs, bins=self.n_clusters)
            clusters_histograms[i] = values

        return clusters_histograms


class BatchedKMeans:
    """
    """
    def __init__(self, n_clusters=200, max_num_passes=10, batch_size=2500):
        print("Init of BatchedKMeans")
        self.n_clusters        = n_clusters
        self.max_num_passes    = max_num_passes
        self.batch_size        = batch_size

    def fit(self, X, y=None):
        """
        Args:
            X: matrix of size (n,300) where is is the number of 
               vectors in the corpus.
        """
        batch_size = np.min([X.shape[0], self.batch_size])
        
        self.kmeans = MiniBatchKMeans(
            n_clusters         = self.n_clusters,
            random_state       = 0,
            max_iter           = 500,
            batch_size         = batch_size,
            tol                = 1, # tune this
            max_no_improvement = 5,
            verbose            = 0
        )
        
        print(f"Fitting BatchedKMeans with {self.n_clusters} clusters.")
        print(f"Mini batch size: {batch_size}")
        print(f"Dataset size: {X.shape[0]}")
        
        # Inertia of the last run
        old_score = 0

        # Number of failed passes
        failed_passes = 0
        
        # Split into kind of equally sized chunks
        limits = np.linspace(
            batch_size,
            X.shape[0],
            int(np.ceil(X.shape[0]/batch_size)),
            dtype=int
        )
        
        print(f"Limits: {limits}")
        
        best_silhouette_score = -float("inf")
        
        for i in range(self.max_num_passes):
        
            print(f'\nPass {i+1} over the dataset.')
            
            np.random.shuffle(X)

            start = 0
            for end in tqdm(limits):
                self.kmeans.partial_fit(X[start:end])
                start = end
                        
            s = self.calculate_sampled_silhouette(X)
            print(f'Mean Silhouette score: {np.mean(s):.2f} ± {np.std(s):.4f}')

            if (i > 0):
                if (np.mean(s) - old_score) < SILHOUETTE_TOL:
                    failed_passes += 1
                    print(
                        f"Breaking training because score is decreasing "
                        f"or isn't improving, failed passes: {failed_passes}."
                    )
                    if failed_passes > MAX_FAILED_PASSES:
                        print(
                            f"Stopping multiple dataset passes because there "
                            f"has been no improvement in {failed_passes} passes."
                        )
                    break
                else:
                    old_score = np.mean(s)
                    failed_passes = 0
        
        return self
        
    def predict(self, X):
        """
        """
        return self.kmeans.predict(X)

    def calculate_sampled_silhouette(self, X):
        """
        Calculate the Silhouette score of this KMeans trained instance in a 
        sample of observations, multiple times.
        It's neccesary to sample because otherwise the time it takes to compute
        the whole dataset is huge.
        """

        print(f'Calculating average sampled Silhouette score...')
        
        if X.shape[0] < self.batch_size:
            clusters_idxs = self.kmeans.predict(X)
            return [silhouette_score(X, clusters_idxs)]

        else:
            s = []
            for _ in range(SILHOUETTE_N_SAMPLES):
                
                sample_idxs = random.sample(
                    range(X.shape[0]),
                    SILHOUETTE_SAMPLE_SIZE
                )

                X_sample = X[sample_idxs, :]
                clusters_idxs_sample = self.kmeans.predict(X_sample)

                silhouette_avg = silhouette_score(
                    X_sample,
                    clusters_idxs_sample
                )
                
                s.append(silhouette_avg)

            return s