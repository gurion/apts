import requests as req
from bs4 import BeautifulSoup as bs
import csv
import json
import re

BASE_URL = 'https://www.apartments.com/'
extension = ''


def get_url_list():
    '''return a list of property URLs to parse in a given polygon'''

    soup = get_page(BASE_URL)
    paging = soup.find('div', {'id': 'placardContainer'}).find(
        'div', {'id': 'paging'}).find_all('a')
    start_page = paging[1].text
    last_page = paging[len(pages) - 2].text


def get_page(url):
    request = req.get(url)
    content = request.content
    return bs(content, 'html.parser')


def write_csv():
    '''
    '''


def create_csv_file():
    '''
    '''


def get_policy():
    '''
    '''


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


def remove_commas(string):
    '''
        '''


def get_building_data(property_soup):
    '''
        '''


def main():
    '''
    '''


if __name__ == '__main__':
    main()
