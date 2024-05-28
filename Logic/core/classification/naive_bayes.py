import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


from Logic.core.classification.basic_classifier import BasicClassifier

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from Logic.core.word_embedding.fasttext_model import preprocess_text


class NaiveBayes(BasicClassifier):
    def __init__(self, count_vectorizer, alpha=1):
        super().__init__()
        self.cv = count_vectorizer
        self.num_classes = None
        self.classes = None
        self.number_of_features = None
        self.number_of_samples = None
        self.prior = None
        self.feature_probabilities = None
        self.log_probs = None
        self.alpha = alpha

    def fit(self, x, y):
        """
        Fit the features and the labels
        Calculate prior and feature probabilities

        Parameters
        ----------
        x: np.ndarray
            An m * n matrix - m is count of docs and n is embedding size

        y: np.ndarray
            The real class label for each doc

        Returns
        -------
        self
            Returns self as a classifier
        """
        self.number_of_samples, self.number_of_features = x.shape
        self.num_classes = len(np.unique(y))
        self.classes = np.unique(y)

        # Calculate prior probabilities
        self.prior = np.zeros(self.num_classes)
        for i, c in enumerate(self.classes):
            self.prior[i] = np.sum(y == c) / self.number_of_samples

        # Calculate feature probabilities
        self.feature_probabilities = np.zeros((self.num_classes, self.number_of_features))
        for i, c in enumerate(self.classes):
            class_indices = np.where(y == c)[0]
            class_data = x[class_indices]
            class_total_count = np.sum(class_data)
            self.feature_probabilities[i] = (np.sum(class_data, axis=0) + self.alpha) / (
                        class_total_count + self.alpha * self.number_of_features)

        # Calculate log probabilities for faster computation
        self.log_probs = np.log(self.feature_probabilities)

        return self

    def predict(self, x):
        """
        Parameters
        ----------
        x: np.ndarray
            An k * n matrix - k is count of docs and n is embedding size
        Returns
        -------
        np.ndarray
            Return the predicted class for each doc
            with the highest probability (argmax)
        """
        log_prior = np.log(self.prior)
        log_likelihood = x @ self.log_probs.T
        log_posterior = log_prior + log_likelihood
        return self.classes[np.argmax(log_posterior, axis=1)]

    def prediction_report(self, x, y):
        """
        Parameters
        ----------
        x: np.ndarray
            An k * n matrix - k is count of docs and n is embedding size
        y: np.ndarray
            The real class label for each doc
        Returns
        -------
        str
            Return the classification report
        """
        predicted = self.predict(x)
        report = classification_report(y, predicted)
        return report

    def get_percent_of_positive_reviews(self, sentences):
        """
        You have to override this method because we are using a different embedding method in this class.
        """
        x = self.cv.transform(sentences)
        y_pred = self.predict(x.toarray())
        positive_reviews = np.sum(y_pred == 1)
        return positive_reviews / len(sentences)


# F1 Accuracy : 85%
if __name__ == '__main__':
    """
    First, find the embeddings of the revies using the CountVectorizer, then fit the model with the training data.
    Finally, predict the test data and print the classification report
    You can use scikit-learn's CountVectorizer to find the embeddings.
    """
    df = pd.read_csv('/Users/alialvandi/Desktop/MIR/Logic/IMDB Dataset.csv')
    reviews = [preprocess_text(text.split()) for text in df['review']]

    sentiments = df['sentiment'].values
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(sentiments)

    count_vectorizer = CountVectorizer(max_features=5000)
    X = count_vectorizer.fit_transform(reviews).toarray()

    X_train, X_test, y_train, y_test = train_test_split(X, sentiments, test_size=0.2, random_state=42)

    nb_classifier = NaiveBayes(count_vectorizer)
    nb_classifier.fit(X_train, y_train)

    print(nb_classifier.prediction_report(X_test, y_test))

