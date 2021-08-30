from bs4 import BeautifulSoup
import requests
from ..database.models import BikeModel
import time
from ..utils.logger import Logger
import math
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Scrapper:

    source_name = None  # source of the data

    base_url = None

    sleep_for = 3

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

            self.extract(html)

            self.logger.info(f'Finished Processing Page No.: {i+1}')
            time.sleep(self.sleep_for)

        self.logger.info(
            f'Total Data Scrapped from { self.source_name if self.source_name else self.base_url } : {len(self.data)}')

    def save(self, model_name: str, model_year: str, kms_driven: str, location: str, price: str, owner: str, db=True):
        bike = {
            'model_name': model_name,
            'model_year': model_year,
            'kms_driven': kms_driven,
            'owner': owner,
            'location': location,
            'price': price
        }
        self.model.save(bike)

        self.data.append(bike)


class BikeWaleScrapper(Scrapper):
    """Scraps the data from www.bikewale.com"""
    base_url = "https://www.bikewale.com/used/bikes-in-india/"

    source_name = 'bikewale.com'

    pagination = 'page-{}/'

    total_pages = 67

    sleep_for = 2

    data = []

    def __init__(self):
        super().__init__()

    def get_total_pages(self):
        return self.total_pages

    def extract(self, html_document):
        
        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')

        bike_list_ele = soup.find('ul', id='used-bikes-list')

        if not bike_list_ele:
            return

        bike_list = bike_list_ele.find_all('li')

        for bike in bike_list:
            tags = bike.find_all('span', class_='model-details-label')

            # for tag in tags
            try:
                model_name = bike.h2.text.split(',')[1]
                model_year = tags[0].text
                kms_driven = tags[1].text
                owner = tags[2].text
                location = tags[3].text
            except IndexError as e:
                self.logger.error(
                    f'Error occured while processing,skipping this record; {e}',)
                continue

            price = bike.find('span', class_='font22').text

            self.save(model_name, model_year,
                      kms_driven, location, price, owner)


class CarAndBikeScrapper(Scrapper):
    """Scraps the data from www.bikewale.com"""
    base_url = "https://www.carandbike.com/used/bikes-for-sale/"

    source_name = 'carandbike.com'

    pagination = '{}/'

    per_page = 18

    def __init__(self):
        super().__init__()

    def get_total_pages(self):
        html_document = self.get_html_document(self.base_url)
        soup = BeautifulSoup(html_document, 'lxml')
        total_bikes_title = soup.find('h1', class_='title-page').text

        if total_bikes_title:
            try:
                total = int(total_bikes_title.split()[0])
            except Exception as e:
                self.logger.error(str(e))
                return 0

            return math.floor(total / self.per_page)

        return 0

    def extract(self, html_document):

        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')

        bike_list = soup.find('div', class_='clist__main').find_all(
            'div', class_='usedcar-widget')

        for bike in bike_list:
            title = bike.find('h4', class_='usedcar-widget__ttl').text
            # title contains model year & model name
            title_splits = title.split()
            model_year = title_splits[0]

            title_splits.pop(0)
            model_name = " ".join(title_splits)

            price = bike.find('div', class_='usedcar-widget__price').text

            location = bike.find('div', class_='usedcar-widget__loc-txt').text

            kms_owner_info = bike.find(
                'ul', class_='usedcar-widget__infolist').find_all('li')

            kms_driven = kms_owner_info[0].text

            owner = kms_owner_info[2].text

            # print(model_name,model_year,kms_driven,owner,location,price)
            self.save(model_name, model_year,
                      kms_driven, location, price, owner)


class Bikes24Scrapper(Scrapper):
    """Scraps the data from www.bikes24.com"""
    base_url = "https://www.bikes24.com/buy-used-bikes-faridabad/"

    source_name = 'bikes24.com'

    pagination = None

    per_page = None

    def __init__(self):
        super().__init__()
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(chrome_options=self.options)

    def get_total_pages(self):
        return 1

    def extract(self, html_document):
        model_name = None
        model_year = None
        kms_driven = None
        owner = None
        # constant location as the location needs to be set manually but all shows same result
        location = 'Delhi'
        price = None

        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')
        # Details are inside the col-4 class div
        bike_list = soup.find_all('div', class_='col-4')

        for bike in bike_list:

            model_name_ele = bike.find('h5')

            if model_name_ele:
                # headline has model year & model name info
                splits = model_name_ele.text.split(' ')
                model_name = splits[1]
                model_year = splits[0]

            price_ele = bike.find('h3')
            if price_ele:
                price = price_ele.text

            # inside the p tag there are spans contains info about the kms driven and owner
            para = bike.find('p')

            if para:
                spans = para.find_all('span')
                if spans:
                    kms_driven = spans[0].text
                    owner = spans[1].text

            if model_name and model_year and kms_driven and owner and location and price:
                # print(model_name,model_year,kms_driven,owner,location,price)
                self.save(model_name, model_year,
                          kms_driven, location, price, owner)

    def start(self):
        self.driver.get(self.base_url)
        time.sleep(2)
        first_popup = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[1]/div[2]/div/div/h3/div/img')

        first_popup.click()

        time.sleep(2)

        html = self.driver.find_element_by_tag_name('html')

        for i in range(10):
            html.send_keys(Keys.END)
            time.sleep(5)

        bike_list = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div[2]/div').get_attribute('innerHTML')

        self.driver.close()

        self.extract(bike_list)


class DroomScrapper(Scrapper):
    """Scraps the data from www.droom.in"""
    base_url = "https://droom.in/bikes/used"

    source_name = 'droom.in'

    pagination = '?page={}&tab=grid&display_category=All+Motorcycles&condition=used/'

    per_page = 20

    def __init__(self):
        super().__init__()

    def get_total_pages(self):
        return 120

    def extract(self, html_document):

        model_name = None
        model_year = None
        kms_driven = None
        owner = None

        location = None
        price = None

        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')

        bike_list = soup.find('div', id='search_results').find_all(
            'div', class_='col-lg-3')

        for bike in bike_list:
            title = bike.find('h4', class_='heading')

            if title:
                title_splits = title.text.split()
                model_year = title_splits[-1]
                title_splits.pop(-1)
                model_name = ' '.join(title_splits)

            price_ele = bike.find('div', class_='price')

            if price_ele:
                price = price_ele.text

            # find kms driven
            labels = bike.find_all('label', class_='d-display-block')

            if labels:
                kms_driven = labels[0].text.strip()
                location = labels[3].text.strip()
                owner = labels[4].text.strip()

            if model_name and model_year and kms_driven and owner and location and price:
                # print(model_name, model_year, kms_driven, owner, location, price)
                self.save(model_name, model_year,
                          kms_driven, location, price, owner)


def start_scrapper():
    # scrap from bikewale
    bikewale_scrapper = BikeWaleScrapper()

    bikewale_scrapper.start()

    # start scrapping from carandbike
    # it shows different result based on different location passed via cookies
    locations = ['New Delhi','Mumbai','Bangalore','Chennai','Hyderabad','Ahmedabad','Kolkata']

    for loc in locations:
        scrapper = CarAndBikeScrapper()
        scrapper.cookies = {'userCity':loc}
        scrapper.start()

    # scrap from bikes24
    bikes24_scrapper = Bikes24Scrapper()

    bikes24_scrapper.start()

    # scrap from droom
    droom_scrapper = DroomScrapper()

    droom_scrapper.start()

if __name__ == '__main__':
    start_scrapper()
    
