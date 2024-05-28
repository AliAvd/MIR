from nltk.corpus import stopwords
class Snippet:
    def __init__(self, number_of_words_on_each_side=5):
        """
        Initialize the Snippet

        Parameters
        ----------
        number_of_words_on_each_side : int
            The number of words on each side of the query word in the doc to be presented in the snippet.
        """
        self.stop_words = set(stopwords.words('english'))
        self.number_of_words_on_each_side = number_of_words_on_each_side

    def remove_stop_words_from_query(self, query):
        """
        Remove stop words from the input string.

        Parameters
        ----------
        query : str
            The query that you need to delete stop words from.

        Returns
        -------
        str
            The query without stop words.
        """

        words = query.split()
        terms = []
        for word in words:
            if word.lower() not in self.stop_words:
                terms.append(word)

        return " ".join(terms)

    def find_snippet(self, doc, query):
        """
        Find snippet in a doc based on a query.

        Parameters
        ----------
        doc : str
            The retrieved doc which the snippet should be extracted from that.
        query : str
            The query which the snippet should be extracted based on that.

        Returns
        -------
        final_snippet : str
            The final extracted snippet. IMPORTANT: The keyword should be wrapped by *** on both sides.
            For example: Sahwshank ***redemption*** is one of ... (for query: redemption)
        not_exist_words : list
            Words in the query which don't exist in the doc.
        """
        final_snippet = ""
        not_exist_words = []

        query = self.remove_stop_words_from_query(query)

        doc_tokens = doc.split()
        query_tokens = query.split()

        matches = []
        for token in query_tokens:
            if token in doc_tokens:
                matches.append(token)
            else:
                not_exist_words.append(token)

        snippet_words = []
        for match in matches:
            match_index = doc_tokens.index(match)
            start_index = max(0, match_index - self.number_of_words_on_each_side)
            end_index = min(len(doc_tokens), match_index + self.number_of_words_on_each_side + 1)
            snippet_words.extend(doc_tokens[start_index:end_index])

        for word in snippet_words:
            if word.lower() in matches:
                final_snippet += f" ***{word}***"
            else:
                final_snippet += f" {word}"

        return final_snippet.strip(), not_exist_words