import wandb
from typing import List


class Evaluation:

    def __init__(self, name: str):
        self.name = name

    def calculate_precision(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The precision of the predicted results
        """
        total_queries = len(actual)
        total_precision = 0.0

        for i in range(total_queries):
            relevant_documents = set(actual[i])
            retrieved_documents = predicted[i]

            relevant_retrieved_documents = [doc for doc in retrieved_documents if doc in relevant_documents]

            query_precision = len(relevant_retrieved_documents) / len(retrieved_documents) if len(
                retrieved_documents) > 0 else 0

            total_precision += query_precision

        precision = total_precision / total_queries if total_queries > 0 else 0.0

        return precision

    def calculate_recall(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the recall of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The recall of the predicted results
        """
        total_queries = len(actual)
        total_recall = 0.0

        for i in range(total_queries):
            relevant_documents = set(actual[i])
            retrieved_documents = predicted[i]

            relevant_retrieved_documents = [doc for doc in retrieved_documents if doc in relevant_documents]

            query_recall = len(relevant_retrieved_documents) / len(relevant_documents) if len(
                relevant_documents) > 0 else 0

            total_recall += query_recall

        recall = total_recall / total_queries if total_queries > 0 else 0.0

        return recall

    def calculate_F1(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the F1 score of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The F1 score of the predicted results
        """
        f1 = 0.0

        precision = self.calculate_precision(actual, predicted)
        recall = self.calculate_recall(actual, predicted)

        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return f1

    def calculate_AP(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Average Precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Average Precision of the predicted results
        """

        total_queries = len(actual)
        total_AP = 0.0

        for i in range(total_queries):
            relevant_documents = set(actual[i])
            retrieved_documents = predicted[i]

            precision_at_k = 0.0
            num_relevant_docs = 0

            for j, doc in enumerate(retrieved_documents, start=1):
                if doc in relevant_documents:
                    num_relevant_docs += 1
                    precision_at_k += num_relevant_docs / j

            if num_relevant_docs > 0:
                average_precision = precision_at_k / len(relevant_documents)
                total_AP += average_precision

        MAP = total_AP / total_queries if total_queries > 0 else 0.0

        return MAP

    def calculate_MAP(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Average Precision of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Mean Average Precision of the predicted results
        """
        MAP = 0.0

        average_precisions = [self.calculate_AP([actual[i]], [predicted[i]]) for i in range(len(actual))]

        MAP = sum(average_precisions) / len(average_precisions) if len(average_precisions) > 0 else 0.0

        return MAP

    def calculate_DCG(self, relevance_scores: List[int]) -> float:
        """
        Calculates the Discounted Cumulative Gain (DCG) of a list of relevance scores

        Parameters
        ----------
        relevance_scores : List[int]
            The relevance scores of the retrieved documents

        Returns
        -------
        float
            The DCG of the list of relevance scores
        """
        dcg = relevance_scores[0] if relevance_scores else 0.0
        for i in range(1, len(relevance_scores)):
            dcg += relevance_scores[i] / (i + 1)  # Discounting relevance based on rank
        return dcg

    def calculate_DCG(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Normalized Discounted Cumulative Gain (NDCG) of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The DCG of the predicted results
        """
        DCG = 0.0

        total_queries = len(actual)
        total_DCG = 0.0

        for i in range(total_queries):
            relevant_documents = set(actual[i])
            retrieved_documents = predicted[i]

            relevance_scores = [1 if doc in relevant_documents else 0 for doc in retrieved_documents]

            dcg = self.calculate_DCG(relevance_scores)

            total_DCG += dcg

        DCG = total_DCG / total_queries if total_queries > 0 else 0.0

        return DCG

    def calculate_IDCG(self, num_relevant_docs: int) -> float:
        """
        Calculates the Ideal Discounted Cumulative Gain (IDCG) for a given number of relevant documents

        Parameters
        ----------
        num_relevant_docs : int
            The number of relevant documents

        Returns
        -------
        float
            The IDCG for the given number of relevant documents
        """
        idcg = sum(1 / (i + 1) for i in range(num_relevant_docs))
        return idcg

    def calculate_NDCG(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Normalized Discounted Cumulative Gain (NDCG) of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The NDCG of the predicted results
        """
        NDCG = 0.0

        total_queries = len(actual)
        total_NDCG = 0.0

        for i in range(total_queries):
            relevant_documents = set(actual[i])
            retrieved_documents = predicted[i]

            relevance_scores = [1 if doc in relevant_documents else 0 for doc in retrieved_documents]

            dcg = self.calculate_DCG(relevance_scores)

            idcg = self.calculate_IDCG(len(relevant_documents))

            ndcg = dcg / idcg if idcg > 0 else 0.0

            total_NDCG += ndcg

        NDCG = total_NDCG / total_queries if total_queries > 0 else 0.0

        return NDCG

    def calculate_RR(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Reciprocal Rank of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The Reciprocal Rank of the predicted results
        """
        RR = 0.0

        for i, doc in enumerate(predicted, start=1):
            if doc in actual:
                return 1 / i
        return RR

    def calculate_MRR(self, actual: List[List[str]], predicted: List[List[str]]) -> float:
        """
        Calculates the Mean Reciprocal Rank of the predicted results

        Parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        Returns
        -------
        float
            The MRR of the predicted results
        """
        MRR = 0.0

        total_queries = len(actual)
        total_rr = 0.0

        for i in range(total_queries):
            rr = self.calculate_RR(actual[i], predicted[i])
            total_rr += rr

        MRR = total_rr / total_queries if total_queries > 0 else 0.0

        return MRR

    def print_evaluation(self, precision, recall, f1, ap, map, dcg, ndcg, rr, mrr):
        """
        Prints the evaluation metrics

        parameters
        ----------
        precision : float
            The precision of the predicted results
        recall : float
            The recall of the predicted results
        f1 : float
            The F1 score of the predicted results
        ap : float
            The Average Precision of the predicted results
        map : float
            The Mean Average Precision of the predicted results
        dcg: float
            The Discounted Cumulative Gain of the predicted results
        ndcg : float
            The Normalized Discounted Cumulative Gain of the predicted results
        rr: float
            The Reciprocal Rank of the predicted results
        mrr : float
            The Mean Reciprocal Rank of the predicted results

        """
        print(f"name = {self.name}")

        print(f"name = {self.name}")
        print(f"Precision: {precision}")
        print(f"Recall: {recall}")
        print(f"F1 Score: {f1}")
        print(f"Average Precision: {ap}")
        print(f"Mean Average Precision: {map}")
        print(f"Discounted Cumulative Gain: {dcg}")
        print(f"Normalized Discounted Cumulative Gain: {ndcg}")
        print(f"Reciprocal Rank: {rr}")
        print(f"Mean Reciprocal Rank: {mrr}")

    def log_evaluation(self, precision, recall, f1, ap, map, dcg, ndcg, rr, mrr):
        """
        Use Wandb to log the evaluation metrics

        parameters
        ----------
        precision : float
            The precision of the predicted results
        recall : float
            The recall of the predicted results
        f1 : float
            The F1 score of the predicted results
        ap : float
            The Average Precision of the predicted results
        map : float
            The Mean Average Precision of the predicted results
        dcg: float
            The Discounted Cumulative Gain of the predicted results
        ndcg : float
            The Normalized Discounted Cumulative Gain of the predicted results
        rr: float
            The Reciprocal Rank of the predicted results
        mrr : float
            The Mean Reciprocal Rank of the predicted results

        """

        wandb.init('MIR_Project')
        wandb.log({
            "Precision": precision,
            "Recall": recall,
            "F1 Score": f1,
            "Average Precision": ap,
            "Mean Average Precision": map,
            "Discounted Cumulative Gain": dcg,
            "Normalized Discounted Cumulative Gain": ndcg,
            "Reciprocal Rank": rr,
            "Mean Reciprocal Rank": mrr
        })

    def calculate_evaluation(self, actual: List[List[str]], predicted: List[List[str]]):
        """
        call all functions to calculate evaluation metrics

        parameters
        ----------
        actual : List[List[str]]
            The actual results
        predicted : List[List[str]]
            The predicted results

        """

        precision = self.calculate_precision(actual, predicted)
        recall = self.calculate_recall(actual, predicted)
        f1 = self.calculate_F1(actual, predicted)
        ap = self.calculate_AP(actual, predicted)
        map_score = self.calculate_MAP(actual, predicted)
        dcg = self.calculate_DCG(actual, predicted)
        ndcg = self.calculate_NDCG(actual, predicted)
        rr = self.calculate_RR(actual, predicted)
        mrr = self.calculate_MRR(actual, predicted)

        # call print and visualize functions
        self.print_evaluation(precision, recall, f1, ap, map_score, dcg, ndcg, rr, mrr)
        self.log_evaluation(precision, recall, f1, ap, map_score, dcg, ndcg, rr, mrr)



