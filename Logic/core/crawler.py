from requests import get
from bs4 import BeautifulSoup
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
import json


class IMDbCrawler:
    """
    put your own user agent in the headers
    """
    headers = {
        'User-Agent': 'https://myip.ms/view/comp_browseragents/5306593/Mozilla_5_0_Macintosh_Intel_Mac_OS_X_12_2_1_AppleWebKit_537_36_KHTML_like_Gecko_Chrome_122_0_0_0_Safari_537_36.html'
    }
    top_250_URL = 'https://www.imdb.com/chart/top/'

    def __init__(self, crawling_threshold=1000):
        """
        Initialize the crawler

        Parameters
        ----------
        crawling_threshold: int
            The number of pages to crawl
        """
        # TODO
        self.crawling_threshold = crawling_threshold
        self.not_crawled = deque()
        self.crawled = set()
        self.added_ids = set()
        self.add_list_lock = Lock()
        self.add_queue_lock = Lock()

    def get_id_from_URL(self, URL):
        """
        Get the id from the URL of the site. The id is what comes exactly after title.
        for example the id for the movie https://www.imdb.com/title/tt0111161/?ref_=chttp_t_1 is tt0111161.

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        str
            The id of the site
        """
        # TODO
        return URL.split('/')[4]

    def write_to_file_as_json(self):
        """
        Save the crawled files into json
        """
        # TODO
        data = {
            'crawled': list(self.crawled),
            'uncrawled': list(self.not_crawled),
            'added_ids': list(self.added_ids)
        }

        with open('imdb_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def read_from_file_as_json(self):
        """
        Read the crawled files from json
        """
        # TODO
        try:
            with open('imdb_data.json', 'r') as json_file:
                data = json.load(json_file)

                # Update the attributes with the data read from the JSON file
                self.crawled = set(data.get('crawled', []))
                self.not_crawled = deque(data.get('uncrawled', []))
                self.added_ids = set(data.get('added_ids', []))
        except FileNotFoundError:
            # If the file is not found, handle the exception gracefully
            print("JSON file not found. No data read.")


    def crawl(self, URL):
        """
        Make a get request to the URL and return the response

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        requests.models.Response
            The response of the get request
        """
        # TODO
        response = get(URL, headers=self.headers)
        return response

    def extract_top_250(self):
        """
        Extract the top 250 movies from the top 250 page and use them as seed for the crawler to start crawling.
        """
        # TODO update self.not_crawled and self.added_ids
        try:
            response = self.crawl(self.top_250_URL)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                movie_links = soup.select('.titleColumn a')

                for link in movie_links:
                    movie_id = self.get_id_from_URL(link['href'])
                    if movie_id not in self.added_ids:
                        self.not_crawled.append(link['href'])
                        self.added_ids.add(movie_id)
        except Exception as e:
            # Handle exceptions gracefully
            print(f"An error occurred while extracting top 250 movies: {e}")


    def get_imdb_instance(self):
        return {
            'id': None,  # str
            'title': None,  # str
            'first_page_summary': None,  # str
            'release_year': None,  # str
            'mpaa': None,  # str
            'budget': None,  # str
            'gross_worldwide': None,  # str
            'rating': None,  # str
            'directors': None,  # List[str]
            'writers': None,  # List[str]
            'stars': None,  # List[str]
            'related_links': None,  # List[str]
            'genres': None,  # List[str]
            'languages': None,  # List[str]
            'countries_of_origin': None,  # List[str]
            'summaries': None,  # List[str]
            'synopsis': None,  # List[str]
            'reviews': None,  # List[List[str]]
        }

    def start_crawling(self):
        """
        Start crawling the movies until the crawling threshold is reached.
        TODO: 
            replace WHILE_LOOP_CONSTRAINTS with the proper constraints for the while loop.
            replace NEW_URL with the new URL to crawl.
            replace THERE_IS_NOTHING_TO_CRAWL with the condition to check if there is nothing to crawl.
            delete help variables.

        ThreadPoolExecutor is used to make the crawler faster by using multiple threads to crawl the pages.
        You are free to use it or not. If used, not to forget safe access to the shared resources.
        """

        # help variables
        WHILE_LOOP_CONSTRAINTS = None
        NEW_URL = None
        THERE_IS_NOTHING_TO_CRAWL = None

        self.extract_top_250()
        futures = []
        crawled_counter = 0

        with ThreadPoolExecutor(max_workers=20) as executor:
            while len(self.not_crawled) > 0 and crawled_counter < self.crawling_threshold:
                URL = self.not_crawled.popleft()
                futures.append(executor.submit(self.crawl_page_info, URL))
                crawled_counter += 1
                if len(self.not_crawled) == 0:
                    wait(futures)
                    futures = []
            wait(futures)

    def crawl_page_info(self, URL):
        """
        Main Logic of the crawler. It crawls the page and extracts the information of the movie.
        Use related links of a movie to crawl more movies.
        
        Parameters
        ----------
        URL: str
            The URL of the site
        """
        print("new iteration")
        # TODO
        response = self.crawl(URL)
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')


    def extract_movie_info(self, res, movie, URL):
        """
        Extract the information of the movie from the response and save it in the movie instance.

        Parameters
        ----------
        res: requests.models.Response
            The response of the get request
        movie: dict
            The instance of the movie
        URL: str
            The URL of the site
        """
        # TODO
        movie['title'] = None
        movie['first_page_summary'] = None
        movie['release_year'] = None
        movie['mpaa'] = None
        movie['budget'] = None
        movie['gross_worldwide'] = None
        movie['directors'] = None
        movie['writers'] = None
        movie['stars'] = None
        movie['related_links'] = None
        movie['genres'] = None
        movie['languages'] = None
        movie['countries_of_origin'] = None
        movie['rating'] = None
        movie['summaries'] = None
        movie['synopsis'] = None
        movie['reviews'] = None

    def get_summary_link(self,url):
        """
        Get the link to the summary page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/plotsummary is the summary page

        Parameters
        ----------
        url: str
            The URL of the site
        Returns
        ----------
        str
            The URL of the summary page
        """
        try:
            # TODO
            movie_id = self.get_id_from_URL(url)
            return f'https://www.imdb.com/title/{movie_id}/plotsummary'
        except:
            print("failed to get summary link")
            return ''

    def get_review_link(self, url):
        """
        Get the link to the review page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/reviews is the review page
        """
        try:
            # TODO
            movie_id = self.get_id_from_URL(url)
            return f'https://www.imdb.com/title/{movie_id}/reviews'
        except:
            print("failed to get review link")
            return ''

    def get_title(soup):
        """
        Get the title of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The title of the movie

        """
        try:
            # TODO
            return soup.find('h1').text.strip()
        except:
            print("failed to get title")
            return ''

    def get_first_page_summary(soup):
        """
        Get the first page summary of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The first page summary of the movie
        """
        try:
            # TODO
            summary = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])['description']
            return summary.strip()
        except:
            print("failed to get first page summary")
            return []

    def get_director(soup):
        """
        Get the directors of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The directors of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])['director']
            directors = []
            for i in range(len(contents)):
                directors.append(contents[i]['name'].strip())
            if len(directors) > 0:
                return directors
            return []
        except:
            print("failed to get director")
            return []

    def get_stars(soup):
        """
        Get the stars of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The stars of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])['actor']
            actors = []
            for i in range(len(contents)):
                actors.append(contents[i]['name'].strip())
            if len(actors) > 0:
                return actors
            return []
        except:
            print("failed to get stars")
            return []

    def get_writers(soup):
        """
        Get the writers of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The writers of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])['creator']
            writers = []
            for i in range(len(contents)):
                if contents[i]['@type'] == 'Person':
                    writers.append(contents[i]['name'].strip())
            if len(writers) > 0:
                return writers
            return []
        except:
            print("failed to get writers")
            return []

    def get_related_links(soup):
        """
        Get the related links of the movie from the More like this section of the page from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The related links of the movie
        """
        try:
            # TODO
            links = soup.findAll('a', {'class': "ipc-poster-card__title ipc-poster-card__title--clamp-2 ipc-poster-card__title--clickable"})
            related_links = []
            for link in links:
                related_links.append("https://www.imdb.com/" + link['href'])
            return related_links

        except:
            print("failed to get related links")
            return []

    def get_summary(self, url):
        """
        Get the summary of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The summary of the movie
        """
        try:
            # TODO
            summaries = []
            summary_plot = self.get_summary_link(url)
            res = self.crawl(summary_plot)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                contents = json.loads(soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
                contents = contents['props']['pageProps']['contentData']['categories'][0]['section']['items']
                for content in contents:
                    summaries.append(content['htmlContent'])
                if len(summaries) > 0:
                    return summaries
                return []
        except:
            print("failed to get summary")
            return []

    def get_synopsis(self,url):
        """
        Get the synopsis of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The synopsis of the movie
        """
        try:
            # TODO
            summary_plot = self.get_summary_link(url)
            res = self.crawl(summary_plot)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                content = json.loads(
                    soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
                content = content['props']['pageProps']['contentData']['categories'][1]['section']['items'][0]['htmlContent']
                if content:
                    return [content]
                return []
        except:
            print("failed to get synopsis")
            return []

    def get_reviews_with_scores(self, url):
        """
        Get the reviews of the movie from the soup
        reviews structure: [[review,score]]

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[List[str]]
            The reviews of the movie
        """
        try:
            # TODO
            review_page = self.get_review_link(url)
            res = self.crawl(review_page)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                contents = soup.select('div[class^="lister-item mode-detail imdb-user-review collapsable"]')
                reviews = []
                for div in contents:
                    inner_div = div.find('div', class_='review-container')
                    text_div = inner_div.find('div', class_='lister-item-content')
                    review_div = text_div.find('div', class_='text show-more__control')
                    review = review_div.text
                    rate_div = text_div.find('div', class_='ipl-ratings-bar')
                    if rate_div:
                        rate_span = rate_div.find('span', class_='rating-other-user-rating')
                        rate = rate_span.text
                        reviews.append((review, rate))
                    else:
                        reviews.append((review, 'No Rating'))
                return reviews


        except:
            print("failed to get reviews")
            return []

    def get_genres(soup):
        """
        Get the genres of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The genres of the movie
        """
        try:
            # TODO
            genres = []
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])['genre']
            for i in range(len(contents)):
                genres.append(contents[i].strip())
            return genres
        except:
            print("Failed to get generes")
            return []

    def get_rating(soup):
        """
        Get the rating of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The rating of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])
            rating = contents['aggregateRating']['ratingValue']
            return str(rating)
        except:
            print("failed to get rating")
            return ''

    def get_mpaa(soup):
        """
        Get the MPAA of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The MPAA of the movie
        """
        try:
            # TODO
            pass
        except:
            print("failed to get mpaa")

    def get_release_year(soup):
        """
        Get the release year of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The release year of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {"type": "application/ld+json"}).contents[0])
            release = contents['datePublished']
            return release
        except:
            print("failed to get release year")
            return ''

    def get_languages(soup):
        """
        Get the languages of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The languages of the movie
        """
        try:
            # TODO
            languages = []
            contents = json.loads(soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
            contents = contents['props']['pageProps']['mainColumnData']['spokenLanguages']['spokenLanguages']
            for content in contents:
                languages.append(content['text'].strip())
            return languages

        except:
            print("failed to get languages")
            return []

    def get_countries_of_origin(soup):
        """
        Get the countries of origin of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The countries of origin of the movie
        """
        try:
            # TODO
            countries = []
            contents = json.loads(soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
            contents = contents['props']['pageProps']['mainColumnData']['countriesOfOrigin']['countries']
            for content in contents:
                countries.append(content['text'].strip())
            return countries
        except:
            print("failed to get countries of origin")
            return []

    def get_budget(soup):
        """
        Get the budget of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The budget of the movie
        """
        try:
            # TODO
            budget = None
            contents = json.loads(soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
            budget = str(contents['props']['pageProps']['mainColumnData']['productionBudget']['budget']['amount'])
            return budget
        except:
            print("failed to get budget")
            return ''

    def get_gross_worldwide(soup):
        """
        Get the gross worldwide of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The gross worldwide of the movie
        """
        try:
            # TODO
            contents = json.loads(soup.find('script', {'id': '__NEXT_DATA__', "type": "application/json"}).contents[0])
            gross = str(contents['props']['pageProps']['mainColumnData']['worldwideGross']['total']['amount'])
            return gross
        except:
            print("failed to get gross worldwide")
            return ''


def main():
    imdb_crawler = IMDbCrawler(crawling_threshold=600)
    # imdb_crawler.read_from_file_as_json()
    imdb_crawler.start_crawling()
    imdb_crawler.write_to_file_as_json()


if __name__ == '__main__':
    main()
