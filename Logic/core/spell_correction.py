from nltk import word_tokenize
class SpellCorrection:
    def __init__(self, all_documents):
        """
        Initialize the SpellCorrection

        Parameters
        ----------
        all_documents : list of str
            The input documents.
        """
        self.all_shingled_words, self.word_counter = self.shingling_and_counting(all_documents)

    def shingle_word(self, word, k=2):
        """
        Convert a word into a set of shingles.

        Parameters
        ----------
        word : str
            The input word.
        k : int
            The size of each shingle.

        Returns
        -------
        set
            A set of shingles.
        """
        shingles = set()
        
        if len(word) < k:
            shingles.add(word)
        else:
            for i in range(len(word) - k + 1):
                shingles.add(word[i : i + k])

        return shingles
    
    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score.

        Parameters
        ----------
        first_set : set
            First set of shingles.
        second_set : set
            Second set of shingles.

        Returns
        -------
        float
            Jaccard score.
        """

        if len(first_set.union(second_set)) == 0:
            return 0
        else:
            return len(first_set.intersection(second_set)) / len(first_set.union(second_set))


    def shingling_and_counting(self, all_documents):
        """
        Shingle all words of the corpus and count TF of each word.

        Parameters
        ----------
        all_documents : list of str
            The input documents.

        Returns
        -------
        all_shingled_words : dict
            A dictionary from words to their shingle sets.
        word_counter : dict
            A dictionary from words to their TFs.
        """
        all_shingled_words = dict()
        word_counter = dict()

        for doc in all_documents:
            for word in doc.split():
                if word not in all_shingled_words:
                    word_counter[word] = 0
                    all_shingled_words[word] = self.shingle_word(word)
                word_counter[word] += 1
                
        return all_shingled_words, word_counter
    
    def find_nearest_words(self, word):
        """
        Find correct form of a misspelled word.

        Parameters
        ----------
        word : stf
            The misspelled word.

        Returns
        -------
        list of str
            5 nearest words.
        """
        top5_candidates = list()

        shingled_word = self.shingle_word(word)
        similarity_scores = {}

        for word, shingle in self.all_shingled_words.items():
            score = self.jaccard_score(shingled_word, shingle)
            similarity_scores[word] = score

        sorted_words = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
        for i in range(5):
            top5_candidates.append(sorted_words[i][0])
        return top5_candidates
    
    def spell_check(self, query):
        """
        Find correct form of a misspelled query.

        Parameters
        ----------
        query : stf
            The misspelled query.

        Returns
        -------
        str
            Correct form of the query.
        """
        final_result = ""
        query = query.lower()
        for word in word_tokenize(query):
            if word in self.word_counter:
                final_result += word
            else:
                nearest = self.find_nearest_words(word)
                if len(nearest) > 0:
                    shingles = self.shingle_word(word)
                    tmp = 0
                    part = ""
                    for near in nearest:
                        score = self.jaccard_score(shingles, self.shingle_word(near))
                        if score > tmp:
                            tmp = score
                            part = near
                    final_result += " "
                    final_result += part
                else:
                    final_result += " "
                    final_result += word

        return final_result