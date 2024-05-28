import time
import os
import json
import copy
from indexes_enum import Indexes
from Logic.core.preprocess import Preprocessor


class Index:
    def __init__(self, preprocessed_documents: list):
        """
        Create a class for indexing.
        """

        self.preprocessed_documents = preprocessed_documents
        self.terms = []
        self.index = {
            Indexes.DOCUMENTS.value: self.index_documents(),
            Indexes.STARS.value: self.index_stars(),
            Indexes.GENRES.value: self.index_genres(),
            Indexes.SUMMARIES.value: self.index_summaries(),
        }

    def index_documents(self):
        """
        Index the documents based on the document ID. In other words, create a dictionary
        where the key is the document ID and the value is the document.

        Returns
        ----------
        dict
            The index of the documents based on the document ID.
        """

        current_index = {}
        for doc in self.preprocessed_documents:
            id = doc['id']
            current_index[id] = doc

        return current_index

    def index_stars(self):
        """
        Index the documents based on the stars.

        Returns
        ----------
        dict
            The index of the documents based on the stars. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        star_indexes = {}
        for doc in self.preprocessed_documents:
            id = doc['id']
            stars = doc['stars']
            parts = []
            if stars is None:
                return star_indexes
            for star in stars:
                for part in star.split():
                    part = part.lower()
                    parts.append(part)
            for star in stars:
                for part in star.split():
                    part = part.lower()
                    self.terms.append(part)
                    if part not in star_indexes:
                        star_indexes[part] = {}
                    star_indexes[part][id] = parts.count(part)

        return star_indexes

    def index_genres(self):
        """
        Index the documents based on the genres.

        Returns
        ----------
        dict
            The index of the documents based on the genres. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        genre_indexes = {}
        for doc in self.preprocessed_documents:
            id = doc['id']
            genres = doc['genres']
            for i in range(len(genres)):
                genres[i] = genres[i].lower()
            for genre in genres:
                if genre not in genre_indexes:
                    self.terms.append(genre)
                    genre_indexes[genre] = {}
                genre_indexes[genre][id] = genres.count(genre)
        return genre_indexes

    def index_summaries(self):
        """
        Index the documents based on the summaries (not first_page_summary).

        Returns
        ----------
        dict
            The index of the documents based on the summaries. You should also store each terms' tf in each document.
            So the index type is: {term: {document_id: tf}}
        """

        current_index = {}
        for doc in self.preprocessed_documents:
            id = doc['id']
            summaries = doc.get('summaries', [])
            if not summaries is None:
                for summary in summaries:
                    summary = summary.lower()
                    dummy = {}
                    for word in summary.split():
                        dummy[word] = dummy.get(word, 0) + 1
                    for word, freq in dummy.items():
                        if word not in current_index:
                            self.terms.append(word)
                            current_index[word] = {}
                        current_index[word][id] = freq
        return current_index

    def get_posting_list(self, word: str, index_type: str):
        """
        get posting_list of a word

        Parameters
        ----------
        word: str
            word we want to check
        index_type: str
            type of index we want to check (documents, stars, genres, summaries)

        Return
        ----------
        list
            posting list of the word (you should return the list of document IDs that contain the word and ignore the tf)
        """

        try:
            posting_list = list(self.index[index_type][word].keys())
            return posting_list
        except:
            return []

    def add_document_to_index(self, document: dict):
        """
        Add a document to all the indexes

        Parameters
        ----------
        document : dict
            Document to add to all the indexes
        """

        id = document['id']
        self.index[Indexes.DOCUMENTS.value][id] = document


        stars = document.get('stars', [])
        stars_parts = []
        for star in stars:
            for part in star.split():
                part = part.lower()
                stars_parts.append(part)
        for star in stars_parts:
            if star not in self.index[Indexes.STARS.value]:
                self.index[Indexes.STARS.value][star] = {}
            self.index[Indexes.STARS.value][star][id] = stars_parts.count(star)


        genres = document.get('genres', [])
        genres_parts = []
        for i in range(len(genres)):
            genres[i] = genres[i].lower()
        for genre in genres:
            if genre not in self.index[Indexes.GENRES.value]:
                self.index[Indexes.GENRES.value][genre] = {}
            self.index[Indexes.GENRES.value][genre][id] = genres.count(genre)

        summaries = document.get('summaries', [])
        for summary in summaries:
            words = summary.split()
            for word in words:
                if word not in self.index[Indexes.SUMMARIES.value]:
                    self.index[Indexes.SUMMARIES.value][word] = {}
                if id not in self.index[Indexes.SUMMARIES.value][word]:
                    self.index[Indexes.SUMMARIES.value][word][id] = words.count(word)

    def remove_document_from_index(self, document_id: str):
        """
        Remove a document from all the indexes

        Parameters
        ----------
        document_id : str
            ID of the document to remove from all the indexes
        """

        if document_id in self.index['documents']:
            del self.index['documents'][document_id]

        to_delete = []
        for item in self.index['stars']:
            for id in self.index['stars'][item]:
                if document_id == id:
                    to_delete.append(item)
                    break

        for key in to_delete:
            del self.index['stars'][key][document_id]

        to_delete = []
        for item in self.index['genres']:
            for id in self.index['genres'][item]:
                if document_id == id:
                    to_delete.append(item)
                    break

        for key in to_delete:
            del self.index['genres'][key][document_id]

        to_delete = []
        for item in self.index['summaries']:
            for id in self.index['summaries'][item]:
                if document_id == id:
                    to_delete.append(item)
                    break

        for key in to_delete:
            del self.index['summaries'][key][document_id]

    def check_add_remove_is_correct(self):
        """
        Check if the add and remove is correct
        """

        dummy_document = {
            'id': '100',
            'stars': ['tim', 'henry'],
            'genres': ['drama', 'crime'],
            'summaries': ['good']
        }

        index_before_add = copy.deepcopy(self.index)
        self.add_document_to_index(dummy_document)
        index_after_add = copy.deepcopy(self.index)

        if index_after_add[Indexes.DOCUMENTS.value]['100'] != dummy_document:
            print('Add is incorrect, document')
            return

        if (set(index_after_add[Indexes.STARS.value]['tim']).difference(set(index_before_add[Indexes.STARS.value]['tim']))
                != {dummy_document['id']}):
            print('Add is incorrect, tim')
            return

        if (set(index_after_add[Indexes.STARS.value]['henry']).difference(set(index_before_add[Indexes.STARS.value]['henry']))
                != {dummy_document['id']}):
            print('Add is incorrect, henry')
            return
        if (set(index_after_add[Indexes.GENRES.value]['drama']).difference(set(index_before_add[Indexes.GENRES.value]['drama']))
                != {dummy_document['id']}):
            print('Add is incorrect, drama')
            return

        if (set(index_after_add[Indexes.GENRES.value]['crime']).difference(set(index_before_add[Indexes.GENRES.value]['crime']))
                != {dummy_document['id']}):
            print('Add is incorrect, crime')
            return

        if (set(index_after_add[Indexes.SUMMARIES.value]['good']).difference(set(index_before_add[Indexes.SUMMARIES.value]['good']))
                != {dummy_document['id']}):
            print('Add is incorrect, good')
            return

        print('Add is correct')

        self.remove_document_from_index('100')
        index_after_remove = copy.deepcopy(self.index)

        if index_after_remove == index_before_add:
            print('Remove is correct')
        else:
            print('Remove is incorrect')

    def store_index(self, path: str, index_name: str = None):
        """
        Stores the index in a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to store the file
        index_name: str
            name of index we want to store (documents, stars, genres, summaries)
        """

        if not os.path.exists(path):
            os.makedirs(path)

        if index_name not in self.index:
            raise ValueError('Invalid index name')

        else:
            index = self.index[index_name]

            with open(os.path.join(path, index_name + '_' + 'index.json'), 'w') as f:
                json.dump(index, f)

    def load_index(self, path: str):
        """
        Loads the index from a file (such as a JSON file)

        Parameters
        ----------
        path : str
            Path to load the file
        """

        path += '_index.json'
        with open(path, 'r') as file:
            return json.load(file)

    def check_if_index_loaded_correctly(self, index_type: str, loaded_index: dict):
        """
        Check if the index is loaded correctly

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        loaded_index : dict
            The loaded index

        Returns
        ----------
        bool
            True if index is loaded correctly, False otherwise
        """

        return self.index[index_type] == loaded_index

    def check_if_indexing_is_good(self, index_type: str, check_word: str = 'good'):
        """
        Checks if the indexing is good. Do not change this function. You can use this
        function to check if your indexing is correct.

        Parameters
        ----------
        index_type : str
            Type of index to check (documents, stars, genres, summaries)
        check_word : str
            The word to check in the index

        Returns
        ----------
        bool
            True if indexing is good, False otherwise
        """

        # brute force to check check_word in the summaries
        start = time.time()
        docs = []
        for document in self.preprocessed_documents:
            if index_type not in document or document[index_type] is None:
                continue

            for field in document[index_type]:
                if check_word in field:
                    docs.append(document['id'])
                    break

            # if we have found 3 documents with the word, we can break
            if len(docs) == 3:
                break

        end = time.time()
        brute_force_time = end - start

        # check by getting the posting list of the word
        start = time.time()
        # TODO: based on your implementation, you may need to change the following line
        posting_list = self.get_posting_list(check_word, index_type)

        end = time.time()
        implemented_time = end - start

        print('Brute force time: ', brute_force_time)
        print('Implemented time: ', implemented_time)

        if set(docs).issubset(set(posting_list)):
            print('Indexing is correct')

            if implemented_time < brute_force_time:
                print('Indexing is good')
                return True
            else:
                print('Indexing is bad')
                return False
        else:
            print('Indexing is wrong')
            return False



# TODO: Run the class with needed parameters, then run check methods and finally report the results of check methods
file = open('/Users/alialvandi/Desktop/MIR/Logic/IMDB_crawled.json')
movies_dataset = json.load(file)
file.close()
index = Index(movies_dataset)
# index.store_index('/Users/alialvandi/Desktop/MIR/Logic/core/indexer/index')
index.store_index('/Users/alialvandi/Desktop/MIR/Logic/core/indexer/index', index_name=Indexes.DOCUMENTS.value)
index.store_index('/Users/alialvandi/Desktop/MIR/Logic/core/indexer/index', index_name=Indexes.STARS.value)
index.store_index('/Users/alialvandi/Desktop/MIR/Logic/core/indexer/index', index_name=Indexes.GENRES.value)
index.store_index('/Users/alialvandi/Desktop/MIR/Logic/core/indexer/index', index_name=Indexes.SUMMARIES.value)
index.check_add_remove_is_correct()
dummy_document = {
           'id': '100',
           'stars': ['tim', 'henry'],
           'genres': ['drama', 'crime'],
           'summaries': ['good']
       }
index.add_document_to_index(dummy_document)
index.check_if_indexing_is_good(Indexes.STARS.value, check_word='tim')
# index.check_if_index_loaded_correctly()

# path = './index/' + Indexes.DOCUMENTS.value
# x = index.load_index(path)
# print(index.check_if_index_loaded_correctly(Indexes.DOCUMENTS.value, x))
with open('../terms.json', 'w') as f:
   json.dump(index.terms, f)