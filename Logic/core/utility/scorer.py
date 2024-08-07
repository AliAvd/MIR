import numpy as np


class Scorer:
    def __init__(self, index, number_of_documents):
        """
        Initializes the Scorer.

        Parameters
        ----------
        index : dict
            The index to score the documents with.
        number_of_documents : int
            The number of documents in the index.
        """

        self.index = index
        self.idf = {}
        self.N = number_of_documents

    def get_list_of_documents(self, query):
        """
        Returns a list of documents that contain at least one of the terms in the query.

        Parameters
        ----------
        query: List[str]
            The query to be scored

        Returns
        -------
        list
            A list of documents that contain at least one of the terms in the query.

        Note
        ---------
            The current approach is not optimal but we use it due to the indexing structure of the dict we're using.
            If we had pairs of (document_id, tf) sorted by document_id, we could improve this.
                We could initialize a list of pointers, each pointing to the first element of each list.
                Then, we could iterate through the lists in parallel.

        """
        list_of_documents = []
        for term in query:
            if term in self.index.keys():
                list_of_documents.extend(self.index[term].keys())
        return list(set(list_of_documents))

    def get_idf(self, term):
        """
        Returns the inverse document frequency of a term.

        Parameters
        ----------
        term : str
            The term to get the inverse document frequency for.

        Returns
        -------
        float
            The inverse document frequency of the term.

        Note
        -------
            It was better to store dfs in a separate dict in preprocessing.
        """
        idf = self.idf.get(term, None)
        if idf is None:
            fq = len(self.index.get(term, {}))
            if fq == 0:
                idf = 0
            else:
                idf = np.log(self.N / fq)
            self.idf[term] = idf
        return idf

    def get_query_tfs(self, query):
        """
        Returns the term frequencies of the terms in the query.

        Parameters
        ----------
        query : List[str]
            The query to get the term frequencies for.

        Returns
        -------
        dict
            A dictionary of the term frequencies of the terms in the query.
        """
        query_term_freq = {}
        for term in query:
            if term not in list(query_term_freq.keys()):
                query_term_freq[term] = 1
            else:
                query_term_freq[term] += 1
        return query_term_freq

    def compute_scores_with_vector_space_model(self, query, method):
        """
        compute scores with vector space model

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c))
            The method to use for searching.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """
        scores = {}
        doc_ids = self.get_list_of_documents(query)
        document_method = method.split(".")[0]
        query_method = method.split(".")[1]
        query_tfs = self.get_query_tfs(query)

        for doc_id in doc_ids:
            score = self.get_vector_space_model_score(query, query_tfs, doc_id, document_method,
                                                      query_method)
            scores[doc_id] = score

        return scores

    def get_vector_space_model_score(self, query, query_tfs, document_id, document_method, query_method):
        """
        Returns the Vector Space Model score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        query_tfs : dict
            The term frequencies of the terms in the query.
        document_id : str
            The document to calculate the score for.
        document_method : str (n|l)(n|t)(n|c)
            The method to use for the document.
        query_method : str (n|l)(n|t)(n|c)
            The method to use for the query.

        Returns
        -------
        float
            The Vector Space Model score of the document for the query.
        """

        term_freq = []
        idf = []
        query_term_freq = []
        for term in query:
            if term in list(self.index.keys()) and document_id in self.index[term]:
                term_freq.append(self.index[term][document_id])
            else:
                term_freq.append(0)
            idf.append(self.get_idf(term))
            query_term_freq.append(query_tfs[term])

        for i in range(len(term_freq)):
            term_freq[i] += 0.1

        if document_method[0] == 'n':
            doc_score = term_freq
        else:
            doc_score = np.log(term_freq) + 1
        if document_method[1] == 't':
            doc_score = np.multiply(doc_score, idf)
        if document_method[2] == 'c':
            doc_score /= np.linalg.norm(doc_score)

        for i in range(len(query_term_freq)):
            query_term_freq[i] += 0.1
        if query_method[0] == 'n':
            query_score = query_term_freq
        else:
            query_score = np.log(query_term_freq) + 1
        if query_method[1] == 't':
            query_score = np.multiply(query_term_freq, idf)
        if query_method[2] == 'c':
            query_score /= np.linalg.norm(query_score)

        return np.dot(doc_score, query_score)

    def compute_scores_with_okapi_bm25(self, query, average_document_field_length, document_lengths):
        """
        compute scores with okapi bm25

        Parameters
        ----------
        query: List[str]
            The query to be scored
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """

        scores = {}
        for doc_id in self.get_list_of_documents(query):
            score = self.get_okapi_bm25_score(query, doc_id, average_document_field_length, document_lengths)
            scores[doc_id] = score
        return scores

    def get_okapi_bm25_score(self, query, document_id, average_document_field_length, document_lengths):
        """
        Returns the Okapi BM25 score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        document_id : str
            The document to calculate the score for.
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        float
            The Okapi BM25 score of the document for the query.
        """
        # https://github.com/yutayamazaki/okapi-bm25/blob/master/okapi_bm25/bm25.py
        k = 1.2
        b = 0.75
        score = 0.0
        for term in query:
            if term in list(self.index.keys()) and document_id in self.index[term]:
                freq = self.index[term][document_id]
                denumerator = freq + k * (1 - b + b * document_lengths[document_id] / average_document_field_length)
                numerator = self.get_idf(term) * freq * (k + 1)
                score += numerator / denumerator
        return score