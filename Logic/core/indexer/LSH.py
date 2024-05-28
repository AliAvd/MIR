import numpy as np
import itertools
import random
import json

class MinHashLSH:
    def __init__(self, documents, num_hashes):
        """
        Initialize the MinHashLSH

        Parameters
        ----------
        documents : list of str
            The input documents for similarity analysis.
        num_hashes : int
            Number of hashes for mini-hashing.
        """
        self.documents = documents
        self.num_hashes = num_hashes

    def shingle_document(self, document, k=2):
        """
        Convert a document into a set of shingles.

        Parameters
        ----------
        document : str
            The input document.
        k : int
            The size of each shingle.

        Returns
        ----------
        set
            A set of shingles.
        """
        shingles = set()
        tokens = document.split()
        for i in range(len(tokens) - 1):
            shingles.add(tokens[i] + " " + tokens[i + 1])
        return shingles

    def build_characteristic_matrix(self):
        """
        Build the characteristic matrix representing the presence of shingles in documents.

        Returns
        ----------
        numpy.ndarray
            The binary characteristic matrix.
        """
        shingles = []
        for doc in self.documents:
            shingles.append(self.shingle_document(doc))
        all_shingles = list(set().union(*shingles))

        characteristic_matrix = np.zeros((len(shingles), len(all_shingles)))
        for i in range(len(shingles)):
            for j in range(len(all_shingles)):
                if all_shingles[j] in shingles[i]:
                    characteristic_matrix[i, j] = 1
        return characteristic_matrix


    def min_hash_signature(self):
        """
        Perform Min-Hashing to generate hash signatures for documents.

        Returns
        ----------
        numpy.ndarray
            The Min-Hash signatures matrix.
        """
        characteristic_matrix = self.build_characteristic_matrix()
        num_docs, num_shingles = characteristic_matrix.shape
        signature_matrix = np.full((self.num_hashes, num_docs), np.inf)

        for h in range(self.num_hashes):
            hash_func = self._hash_func_generator()
            for doc_index in range(num_docs):
                for shingle_index in range(num_shingles):
                    if characteristic_matrix[doc_index, shingle_index] == 1:
                        hash_val = hash_func(shingle_index)
                        if hash_val < signature_matrix[h, doc_index]:
                            signature_matrix[h, doc_index] = hash_val

        return signature_matrix

    def _hash_func_generator(self):
        seed = np.random.randint(0, 1000)

        def hash_func(x):
            return hash(str(seed) + str(x)) % (2 ** 32 - 1)

        return hash_func

    def lsh_buckets(self, signature, bands=10, rows_per_band=10):
        """
        Group documents into Locality-Sensitive Hashing (LSH) buckets based on Min-Hash signatures.

        Parameters
        ----------
        signature : numpy.ndarray
            Min-Hash signatures for documents.
        bands : int
            Number of bands for LSH.
        rows_per_band : int
            Number of rows per band.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        num_hashes, num_docs = signature.shape
        assert num_hashes % bands == 0, "Number of rows in the signature matrix must be divisible by the number of bands"

        band_size = num_hashes // bands

        buckets = {}
        for band_id in range(bands):
            start_row = band_id * band_size
            end_row = start_row + band_size
            band = signature[start_row:end_row]
            band_hash = self._hash_band(band)
            for doc_index, hash_val in enumerate(band_hash):
                bucket_id = (band_id, hash_val)
                if bucket_id not in buckets:
                    buckets[bucket_id] = []
                buckets[bucket_id].append(doc_index)

        return buckets

    def _hash_band(self, band):
        hash_values = []
        for col in range(band.shape[1]):
            hash_val = hash(tuple(band[:, col]))
            hash_values.append(hash_val)
        return hash_values

    def perform_lsh(self):
        """
        Perform the entire Locality-Sensitive Hashing (LSH) process.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        signature = self.min_hash_signature()
        buckets = self.lsh_buckets(signature)
        return buckets

    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score for two sets.

        Parameters
        ----------
        first_set : set
            Set of first shingled document.
        second_set : set
            Set of second shingled document.

        Returns
        ----------
        float
            Jaccard score.
        """
        intersection = len(first_set.intersection(second_set))
        union = len(first_set.union(second_set))

        if union == 0:
            return 0.0

        return intersection / union

    def jaccard_similarity_test(self, buckets, all_documents):
        """
        Test your near duplicate detection code based on jaccard similarity.

        Parameters
        ----------
        buckets : dict
            A dictionary mapping bucket IDs to lists of document indices.
        all_documents : list
            The input documents for similarity analysis.
        """
        correct_near_duplicates = 0
        all_near_duplicates = 0

        for bucket_id in buckets.keys():
            docs_in_this_bucket = buckets[bucket_id]
            unique_doc_ids = set(docs_in_this_bucket)
            if len(unique_doc_ids) > 1:
                combinations = list(itertools.combinations(unique_doc_ids, 2))
                for comb in combinations:
                    all_near_duplicates += 1

                    first_doc_id = comb[0]
                    second_doc_id = comb[1]

                    first_shingled_doc = self.shingle_document(all_documents[first_doc_id], 2)
                    second_shingled_doc = self.shingle_document(all_documents[second_doc_id], 2)

                    near_duplicated_jaccard_score = self.jaccard_score(first_shingled_doc, second_shingled_doc)
                    current_score = 0

                    for _ in range(5):
                        random_doc_id = first_doc_id
                        while random_doc_id == first_doc_id or random_doc_id == second_doc_id:
                            random_doc_id = random.randint(0, len(all_documents) - 1)
                        random_shingled_doc = self.shingle_document(all_documents[random_doc_id], 2)

                        random_jaccard_score = self.jaccard_score(first_shingled_doc, random_shingled_doc)

                        if near_duplicated_jaccard_score > random_jaccard_score:
                            current_score += 1

                    if current_score == 5:
                        correct_near_duplicates += 1

        # a good score is around 0.8
        print("your final score in near duplicate detection:", correct_near_duplicates / all_near_duplicates)

with open('/Users/alialvandi/Desktop/MIR/Logic/core/LSHFakeData.json', 'r') as file:
    movies = json.load(file)

with open('/Users/alialvandi/Desktop/MIR/Logic/IMDB_crawled.json', 'r') as file:
    all_movies = json.load(file)

docs = []

for movie in movies:
    if not movie['summaries'] is None:
        if len(movie['summaries']) > 0:
            docs.append(' '.join(movie['summaries']))

for movie in all_movies:
    if not movie['summaries'] is None:
        if len(movie['summaries']) > 0:
            docs.append(' '.join(movie['summaries']))

minHashLSH = MinHashLSH(docs, 100)
minHashLSH.jaccard_similarity_test(minHashLSH.perform_lsh(), docs)