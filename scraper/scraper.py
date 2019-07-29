import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import pandas


BASE_URL = 'https://www.apartments.com/'
extension = 'new-york-ny/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
}


def get_url_list():
    '''return a list of property URLs to parse in a given polygon'''
    soup = get_page(BASE_URL + extension)
    page_urls = get_all_page_urls(soup)
    listing_ids = []
    for url in page_urls:
        page = get_page(url)
        listing_ids += get_property_ids_from_page(page)

    return listing_ids


def get_page(url):
    '''get request a page and return beautiful soup object'''
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def get_all_page_urls(soup):
    '''Get all the urls needed to iterate over all the placards'''
    pages = soup.find('div', {'id': 'placardContainer'}).find('div', {'id': 'paging'}).find_all('a')
    start_page = pages[1].text
    last_page = pages[len(pages)-2].text
    return [BASE_URL+extension+str(page_number) for page_number in range(int(start_page), int(last_page) + 1)]


def get_property_ids_from_page(soup):
    '''get list of property listing IDs'''
    placards = soup.find('div', {'id': 'placardContainer'}).find_all('article', {})
    return [placard['data-listingid'] for placard in placards]


def write_csv():
    '''write data structure (in format in testing/data_structure.json) to a csv file'''


def create_csv_file():
    '''create a csv file for writing data'''


def get_policy():
    '''Get building policies - parking, gym, etc.'''


def get_rent(table_row):
    '''get rent given table row tag'''


def get_sqft(table_row):
    '''get square footage given table row tag'''


def get_all_row_data(table_row):
    '''get all the data for a given property'''
    property_dict = {
        'beds': table_row.get('data-beds', -1),
        'baths': table_row.get('data-baths', None),

    }


def get_building_data(property_soup):
    '''
        Get the data from the table of apartments associated with the building
        '''


def main():
    '''
    '''
    get_url_list()


if __name__ == '__main__':
    main()
