from bs4 import BeautifulSoup
import bs4
import requests
import time


class Scrapper:

    source_name = None  # source of the data

    base_url = None

    sleep_for = 3

    cookies = {}

    data = []

    # def __init__(self):
    #     self.model = BikeModel()
    #     self.logger = Logger(__name__, std_out=True)

    def get_html_document(self, url):
        # request for HTML document of given url
        response = requests.get(url, cookies=self.cookies)
        # response will be provided in JSON format
        return response.text

    def get_total_pages(self):
        """Calculate total number of pages to be scrapped"""
        return 1

    def extract(self, html_document):
        model_name = None
        model_year = None
        kms_driven = None
        location = None
        price = None
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
                        mileage = li.text.replace('Mileage','')
                    if 'Engine' in li.text:
                        engine = li.text.strip()
                    if 'Power' in li.text:
                        power = li.text.replace('Max Power','').strip()
                    if 'Wheel' in li.text:
                        wheel_size = li.text.replace('Wheel Size').strip()

                except Exception as e:
                    continue
            #  print('AAAA',owner,kms_driven,mileage,engine,power,wheel_size)
        return {
            'owner': owner,
            'kms_driven': kms_driven,
            'mileage': mileage,
            'engine': engine,
            'power': power,
            'wheel_size': wheel_size
        }

            # self.save(model_name, model_year,
            #           kms_driven, location, price, owner)

    def start(self):

        print(
            f'Start data scrapping from {self.source_name if self.source_name else self.base_url}')
        total_pages = self.get_total_pages()

        for i in range(total_pages):

            print(f'Started Processing Page No.: {i+1}')
            url_to_scrape = "https://droom.in/product/bajaj-avenger-street-220-2017-612e54d9e81bb0cd098b45af"

            html = self.get_html_document(url_to_scrape)
            # print(html)
            print(self.extract(html))

            print(f'Finished Processing Page No.: {i+1}')

            time.sleep(self.sleep_for)


if __name__ == '__main__':

    Scrapper().start()
