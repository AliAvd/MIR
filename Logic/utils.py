from typing import Dict, List
from Logic.core.search import SearchEngine
from Logic.core.spell_correction import SpellCorrection
from Logic.core.snippet import Snippet
from Logic.core.preprocess import Preprocessor
from Logic.core.indexer.indexes_enum import Indexes, Index_types
import json

file = open('/Users/alialvandi/Desktop/MIR/Logic/IMDB_crawled.json')
movies_dataset = json.load(file)
file.close()

file = open('/Users/alialvandi/Desktop/MIR/Logic/core/terms.json')
terms = json.load(file)
file.close()

# movies_dataset = None
# You can refer to `get_movie_by_id` to see how this is used.
search_engine = SearchEngine()


def correct_text(text: str, all_documents: List[str]) -> str:
    """
    Correct the give query text, if it is misspelled using Jacard similarity

    Paramters
    ---------
    text: str
        The query text
    all_documents : list of str
        The input documents.

    Returns
    str
        The corrected form of the given text
    """
    preprocessor = Preprocessor(all_documents)
    all_documents = preprocessor.preprocess()
    spell_correction_obj = SpellCorrection(all_documents)
    text = spell_correction_obj.spell_check(text)
    return text


def search(
    query: str,
    max_result_count: int,
    method: str = "ltn-lnn",
    weights: list = [0.3, 0.3, 0.4],
    should_print=False,
    preferred_genre: str = None,
    smoothing_method=None,
    alpha=0.5,
    lamda=0.5,
):
    """
    Finds relevant documents to query

    Parameters
    ---------------------------------------------------------------------------------------------------
    query:
        The query text

    max_result_count: Return top 'max_result_count' docs which have the highest scores.
                      notice that if max_result_count = -1, then you have to return all docs

    method: 'ltn.lnn' or 'ltc.lnc' or 'OkapiBM25'

    weights:
        The list, containing importance weights in the search result for each of these items:
            Indexes.STARS: weights[0],
            Indexes.GENRES: weights[1],
            Indexes.SUMMARIES: weights[2],

    preferred_genre:
        A list containing preference rates for each genre. If None, the preference rates are equal.
        (You can leave it None for now)

    Returns
    ----------------------------------------------------------------------------------------------------
    list
    Retrieved documents with snippet
    """
    weights = {
        Indexes.STARS: 1,
        Indexes.GENRES: 1,
        Indexes.SUMMARIES: 1
    }
    # return search_engine.search(
    #     query, method, weights, max_results=max_result_count, safe_ranking=True
    # )
    return search_engine.search(query, method, weights, safe_ranking=True, max_results=10, smoothing_method=smoothing_method,
            alpha=alpha,
            lamda=lamda)


def get_movie_by_id(id: str, movies_dataset: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Get movie by its id

    Parameters
    ---------------------------------------------------------------------------------------------------
    id: str
        The id of the movie

    movies_dataset: List[Dict[str, str]]
        The dataset of movies

    Returns
    ----------------------------------------------------------------------------------------------------
    dict
        The movie with the given id
    """
    result = {}
    for movie in movies_dataset:
        if movie['id'] == id:
            result = movie
    result["Image_URL"] = (
        "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg"
    # a default picture for selected movies
    )
    result["URL"] = (
        f"https://www.imdb.com/title/{result['id']}"  # The url pattern of IMDb movies
    )
    return result
    # result = movies_dataset.get(
    #     id,
    #     {
    #         "Title": "This is movie's title",
    #         "Summary": "This is a summary",
    #         "URL": "https://www.imdb.com/title/tt0111161/",
    #         "Cast": ["Morgan Freeman", "Tim Robbins"],
    #         "Genres": ["Drama", "Crime"],
    #         "Image_URL": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg",
    #     },
    # )
    #
    # result["Image_URL"] = (
    #     "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg"  # a default picture for selected movies
    # )
    # result["URL"] = (
    #     f"https://www.imdb.com/title/{result['id']}"  # The url pattern of IMDb movies
    # )
    # return result