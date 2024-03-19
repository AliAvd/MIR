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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
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
        self.crawled = []
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

        with open('../IMDB_crawled.json', 'w') as file:
            json.dump(self.crawled, file)

        with (open('../IMDB_not_crawled.json', 'w') as file):
            json.dump(list(self.not_crawled), file)

    def read_from_file_as_json(self):
        """
        Read the crawled files from json
        """

        with open('../IMDB_crawled.json', 'r') as file:
            crawled_data = json.load(file)
            self.crawled = crawled_data

        with open('../IMDB_not_crawled.json', 'r') as file:
            not_crawled_data = json.load(file)
            self.not_crawled = not_crawled_data

        for data in crawled_data:
            self.added_ids.add(data['id'])

        for data in not_crawled_data:
            self.added_ids.add(self.get_id_from_URL(data))


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
                contents = soup.findAll('a', {'class': "ipc-lockup-overlay ipc-focusable"})
                for content in contents:
                    c = content['href'].split("/")
                    url = 'https://www.imdb.com/' + c[1] + '/' + c[2]
                    id = self.get_id_from_URL(url)
                    if id not in self.added_ids and url not in self.crawled:
                        self.not_crawled.append(url)
                        self.added_ids.add(id)
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

        self.extract_top_250()
        futures = []
        crawled_counter = 0

        with ThreadPoolExecutor(max_workers=20) as executor:
            while len(self.not_crawled) > 0 and crawled_counter < self.crawling_threshold:
                with self.add_queue_lock:
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
            movie = self.get_imdb_instance()
            self.extract_movie_info(soup, movie, URL)
            with self.add_queue_lock:
                self.crawled.append(movie)
                print(len(self.crawled))

            related_links = movie['related_links']
            for link in related_links:
                if link not in self.not_crawled:
                    with self.add_queue_lock:
                        self.not_crawled.append(link)
                    with self.add_list_lock:
                        self.added_ids.add(self.get_id_from_URL(link))

    def extract_movie_info(self, soup, movie, URL):
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
        movie['id'] = self.get_id_from_URL(URL)
        movie['title'] = self.get_title(soup)
        movie['first_page_summary'] = self.get_first_page_summary(soup)
        movie['release_year'] = self.get_release_year(soup)
        movie['mpaa'] = self.get_mpaa(URL)
        movie['budget'] = self.get_budget(soup)
        movie['gross_worldwide'] = self.get_gross_worldwide(soup)
        movie['directors'] = self.get_director(soup)
        movie['writers'] = self.get_writers(soup)
        movie['stars'] = self.get_stars(soup)
        movie['related_links'] = self.get_related_links(soup)
        movie['genres'] = self.get_genres(soup)
        movie['languages'] = self.get_languages(soup)
        movie['countries_of_origin'] = self.get_countries_of_origin(soup)
        movie['rating'] = self.get_rating(soup)
        movie['summaries'] = self.get_summary(URL)
        movie['synopsis'] = self.get_synopsis(URL)
        movie['reviews'] = self.get_reviews_with_scores(URL)

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

    def get_title(self, soup):
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

    def get_first_page_summary(self, soup):
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
            return ''

    def get_director(self, soup):
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
            return directors
        except:
            print("failed to get director")
            return []

    def get_stars(self ,soup):
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
            return actors
        except:
            print("failed to get stars")
            return []

    def get_writers(self, soup):
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
            return writers
        except:
            print("failed to get writers")
            return []

    def get_related_links(self, soup):
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
                return summaries
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

    def get_genres(self, soup):
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

    def get_rating(self, soup):
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
            rating = str(contents['aggregateRating']['ratingValue'])
            if rating:
                return rating
            return ''
        except:
            print("failed to get rating")
            return ''

    def get_mpaa(self, url):
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
            movie_id = self.get_id_from_URL(url)
            new_url = f'https://www.imdb.com/title/{movie_id}/parentalguide'
            res = self.crawl(new_url)
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, 'html.parser')
                content = soup.find('tr', {'id': 'mpaa-rating'})
                mpaa = content.findAll('td')[1].text
                if mpaa:
                    return mpaa
                return ''
        except:
            print("failed to get mpaa")
            return ''

    def get_release_year(self, soup):
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

    def get_languages(self, soup):
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

    def get_countries_of_origin(self, soup):
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

    def get_budget(self, soup):
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
            if budget:
                return budget
            return ''
        except:
            print("failed to get budget")
            return ''

    def get_gross_worldwide(self, soup):
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
            if gross:
                return gross
            return ''
        except:
            print("failed to get gross worldwide")
            return ''


def main():
    imdb_crawler = IMDbCrawler(crawling_threshold=10)
    imdb_crawler.start_crawling()
    imdb_crawler.write_to_file_as_json()


if __name__ == '__main__':
    main()
