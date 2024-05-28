import numpy as np
import pandas as pd
import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from Logic.core.word_embedding.fasttext_model import FastText, preprocess_text


class ReviewLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.fasttext_model = None
        self.review_tokens = []
        self.sentiments = []
        self.embeddings = []

    def load_data(self):
        """
        Load the data from the csv file and preprocess the text. Then save the normalized tokens and the sentiment labels.
        Also, load the fasttext model.
        """
        data = pd.read_csv(self.file_path)

        texts = data['review']
        sentiments = data['sentiment'].values

        preprocessed_texts = [preprocess_text(text.split()) for text in texts]

        self.review_tokens = preprocessed_texts
        self.sentiments = sentiments

        self.fasttext_model = FastText()
        self.fasttext_model.load_model(path='../word_embedding/FastText_model.bin')
        self.get_embeddings()

    def get_embeddings(self):
        """
        Get the embeddings for the reviews using the fasttext model.
        """
        # self.embeddings = [self.fasttext_model.get_query_embedding(tokens) for tokens in self.review_tokens]
        for x in self.review_tokens:
            self.embeddings.append(self.fasttext_model.get_query_embedding(x))

    def split_data(self, test_data_ratio=0.2):
        """
        Split the data into training and testing data.

        Parameters
        ----------
        test_data_ratio: float
            The ratio of the test data
        Returns
        -------
        np.ndarray, np.ndarray, np.ndarray, np.ndarray
            Return the training and testing data for the embeddings and the sentiments.
            in the order of x_train, x_test, y_train, y_test
        """
        label_encoder = LabelEncoder()
        labels = label_encoder.fit_transform(self.sentiments)
        x_train, x_test, y_train, y_test = train_test_split(self.embeddings, labels, test_size=test_data_ratio,
                                                            random_state=42)

        return np.array(x_train), np.array(x_test), np.array(y_train), np.array(y_test)

