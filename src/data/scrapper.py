from bs4 import BeautifulSoup
import requests
from ..database.models import BikeModel, VisitedPageModel  
import time

class Scrapper:
    base_url = "https://www.bikewale.com/used/bikes-in-india/"

    pagination = 'page-{}/'

    total_pages = 67

    sleep_for = 2

    data = []

    def __init__(self) -> None:
        self.model = BikeModel()

    def get_html_document(self,url):
        # request for HTML document of given url
        response = requests.get(url)
        # response will be provided in JSON format
        return response.text

    def extract_info(self,html_document):       
        # create soap object
        soup = BeautifulSoup(html_document, 'lxml')

        bike_list = soup.find('ul',id='used-bikes-list').find_all('li')

        for bike in bike_list:
            # print(bike.h2.text,bike.find('span',class_='model-details-label').text)
            tags = bike.find_all('span',class_='model-details-label')
            
            # for tag in tags
            try:
                model_name = bike.h2.text.split(',')[1]
                model_year = tags[0].text
                kms_driven = tags[1].text
                owner = tags[2].text
                location = tags[3].text
            except IndexError as e:
                print(f'Error occured while processing,skipping this record; ',e)
                continue

            price = bike.find('span',class_='font22').text

            bike = {
                'model_name': model_name,
                'model_year': model_year,
                'kms_driven': kms_driven,
                'owner': owner,
                'location': location,
                'price': price
            }

            self.model.insert(bike)

            self.data.append(bike)

            
    
    def start(self):
        for i in range(self.total_pages):
            print('Started Processing Page No. : ',i+1)
            url_to_scrape = self.base_url + self.pagination.format(i+1)

            html = self.get_html_document(url_to_scrape)

            self.extract_info(html)
            print('Finished Processing Page No. : ',i+1)
            time.sleep(self.sleep_for)



if __name__ == '__main__':
    
    scrapper = Scrapper()

    # scrapper.total_pages = 10
    scrapper.sleep_for = 3

    scrapper.start()

    print('Total Data Scrapped : ',len(scrapper.data))

  