import json
from bs4 import BeautifulSoup
import requests
from ..database.models import BikeModel, UrlVisited
import time
from ..utils.logger import Logger
import math
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Scrapper:

    source_name = None  # source of the data

    base_url = None

    cookies = {}

    data = []

    def __init__(self):
        self.model = BikeModel()
        self.logger = Logger(__name__, std_out=True)

    def get_html_document(self, url):
        # request for HTML document of given url
        response = requests.get(url, cookies=self.cookies)
        # response will be provided in JSON format
        return response.text

    def get_total_pages(self):
        """Calculate total number of pages to be scrapped"""
        return 0

    def extract(self, url: str):
        """Write your own implementation how you will fetch data"""
        raise NotImplemented('extract method is not implemented.')

    def start(self):

        self.logger.info(
            f'Start data scrapping from {self.source_name if self.source_name else self.base_url}')
        total_pages = self.get_total_pages()
        self.logger.info(f'Total Pages To Scrap {total_pages}')
        for i in range(total_pages):

            self.logger.info(f'Started Processing Page No.: {i+1}')
            url_to_scrape = self.base_url + self.pagination.format(i+1)

            html = self.get_html_document(url_to_scrape)
            # print(html)
            self.extract(html)

            self.logger.info(f'Finished Processing Page No.: {i+1}')

            time.sleep(self.sleep_for)

        self.logger.info(
            f'Total Data Scrapped from { self.source_name if self.source_name else self.base_url } : {len(self.data)}')


class DroomScrapper:
    """Scraps the data from www.droom.in"""

    source_name = 'droom.in'

    api_url = 'https://cdnaka.acedms.com/v2/search?bucket=bike&category=Motorcycle%2FBike&condition=used&include_premium=1&page={}&rows_per_page=24&selling_format=fixed_price&status=active'

    per_page = 24

    sleep_for = 1

    data = []

    def __init__(self):
        self.model = BikeModel()
        self.url_visted = UrlVisited()
        self.logger = Logger(__name__, std_out=True)

    def get_html_document(self, url):
        # request for HTML document of given url
        response = requests.get(url)
        # response will be provided in JSON format
        return response.text

    def get_total_pages(self):
        return 1500

    
    def extract_api(self, json_data):

        bike_id = json_data.get('listing_alias')

        model = json_data.get('product_title')

        price = json_data.get('total_payout_value')

        owner = json_data.get('number_of_owners')

        model_year = json_data.get('year')

        locations = json_data.get('location')

        single_loc = None

        if locations:
            single_loc = locations[0]

        # extract other info from details page usig bs4
        base_url = "https://droom.in/product/" + bike_id

        if self.url_visted.find(base_url):
            return

        data = self.extract_html(self.get_html_document(base_url))

        if not data:
            self.logger.info(
                f'Could not find data of {model}.Skipping this...')
            return

        data['model_name'] = model
        data['price'] = price
        data['owner'] = owner
        data['model_year'] = model_year
        data['location'] = single_loc

        self.model.save(data)

        self.logger.info(f'Saving data of {model} to database...')

        self.url_visted.save({'link': base_url})

    def extract_html(self, html_document):
        kms_driven = None
        owner = None
        mileage = None
        engine = None
        power = None
        wheel_size = None

        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')

        # d-display-table d-width-100
        bike_list_ele = soup.find_all(
            'ul', class_='d-display-table d-width-100')

        if not bike_list_ele:
            return

        for details_ul in bike_list_ele:
            for li in details_ul:
                try:
                    if 'Owner' in li.text:
                        owner = li.text.strip()
                    if 'Km' in li.text:
                        kms_driven = li.text.strip()
                    if 'Mileage' in li.text:
                        mileage = li.text.replace('Mileage', '')
                    if 'Engine' in li.text:
                        engine = li.text.replace('Engine')
                    if 'Power' in li.text:
                        power = li.text.replace('Max Power', '').strip()
                    if 'Wheel' in li.text:
                        wheel_size = li.text.replace('Wheel Size').strip()

                except Exception as e:
                    continue

        return {
            'owner': owner,
            'kms_driven': kms_driven,
            'mileage': mileage,
            'engine': engine,
            'power': power,
            'wheel_size': wheel_size
        }

    def start(self):

        self.logger.info(f'Started scrapping data from {self.source_name}')
        self.logger.info(f'Total Pages Found {self.get_total_pages()}.')
        for i in range(self.get_total_pages()):
            self.logger.info(f'Processing page no. {i+1}')

            url = self.api_url.format(i+1)

            if self.url_visted.find(url):
                continue

            response = requests.get(url)

            data = response.json()

            if data.get('data'):
                listings = data.get('data').get('listings')

                if listings:
                    for item in listings:
                        self.extract_api(item)
                        time.sleep(1)

            self.logger.info(f'Processing page no. {i+1}')
            self.url_visted.save({'link': url})
            time.sleep(self.sleep_for)


def start_scrapper():
    droom_scrapper = DroomScrapper()

    droom_scrapper.start()


if __name__ == '__main__':
    start_scrapper()
