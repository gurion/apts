import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import pandas

########## GLOBAL VARS #######################
BASE_URL = 'https://www.apartments.com/'
# This is your unique search identifier from a region
extension = '?sk=5cad1a13429d27fcc6faa34b11b0ddd1&bb=yskr9wknwHzl3_uB/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
}
data = {}
url_dict = {}
##############################################


def get_url_list():
    '''return a list of property URLs to parse in a given polygon'''
    soup = get_page_soup(BASE_URL + extension)
    page_urls = get_all_page_urls(soup)
    for url in page_urls:
        get_property_addresses_and_urls_from_search_page(get_page_soup(url))


def get_page_soup(url):
    '''get request a page and return beautiful soup object'''
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def get_all_page_urls(soup):
    '''Get all the urls needed to iterate over all the placards'''
    try:
        pages = soup.find('div', {'id': 'placardContainer'}).find(
            'div', {'id': 'paging'}).find_all('a')
        start_page = pages[1].text
        last_page = pages[len(pages)-2].text
        return [BASE_URL+extension+str(page_number) for page_number in range(int(start_page), int(last_page) + 1)]
    except AttributeError:
        return [BASE_URL+extension]


def get_property_addresses_and_urls_from_search_page(soup):
    '''get list of listing urls associated with property address'''
    script = soup.find('div', {'class': 'mainWrapper'}).find(
        'script', type='application/ld+json').get_text()
    json_data = json.loads(script)['about']
    properties = {property['url']: get_property_address_from_json(
        property) for property in json_data}
    url_dict.update(properties)


def get_property_address_from_json(property):
    '''given json, extract address'''
    return property['Address']['streetAddress'] + ', ' + property['Address']['addressLocality'] + ', ' + property['Address']['addressRegion'] + ' ' + property['Address']['postalCode']


def add_building_data(address, url):
    '''Get the data from the table of apartments associated with the building'''
    soup = get_page_soup(url)
    address = url_dict[url]
    table_rows = []
    try:
        table_rows = soup.find('div', {'id': 'apartmentsTabContainer'}).find(
            'div', {'class': 'js-expandableContainer'}).find('tbody').find_all('tr')
    except:
        print(url)

    for tr in table_rows:
        unit = get_unit(tr)
        beds = get_beds(tr)
        baths = get_baths(tr)
        rent = get_rent(tr)
        sqft = get_sqft(tr)
        avail = get_avail(tr)
        add_unit(address, unit, beds, baths, rent, sqft, avail)


def get_unit(tr):
    '''get unit number'''
    unit = tr.find('td', {'class': 'name '})
    if unit is None:
        return -1
    return unit.text.strip()


def get_beds(tr):
    '''get number of bedrooms'''
    beds = tr.find('td', {'class': 'beds'}).text.split()[0]
    if beds == 'Studio':
        beds = 0
    return int(beds)


def get_baths(tr):
    '''get number of bathrooms'''
    baths = tr.find('td', {'class': 'baths'}).text.split()[0]
    try:
        return float(baths)
    except ValueError:
        return float(baths[0]) + .5


def get_rent(tr):
    '''get rent'''
    rent = tr.find('td', {'class': 'rent'})
    if rent is None:
        return -1
    return int(rent.text.strip().replace(',', '').strip('$'))


def get_sqft(tr):
    '''get square footage'''
    sqft = tr.find('td', {'class': 'sqft'}).get_text().split()[0]
    if sqft == '':
        return -1
    return int(sqft.strip().replace(',', ''))


def get_avail(tr):
    '''get availability'''
    avail = tr.find('td', {'class': 'available'})
    if avail is None:
        return -1
    avail = 1 if avail.text == 'Available Now' else 0
    return avail


def add_address(address):
    '''add building to database'''
    data.update({
        address: {
            "units": [],
            "policies": {
                "pets": "TBD",
                "parking": "TBD",
                "property_info": "TBD",
                "fitness": "TBD",
                "outdoor": "TBD"
            }
        }
    })


def add_unit(address, unit_num='', beds=-1, baths=-1.0, rent=-1, sqft=-1, avail=-1):
    '''add a unit to the database'''
    data[address]["units"].append({
        "unit": unit_num,
        "beds": beds,
        "baths": baths,
        "rent": rent,
        "sqft": sqft,
        "avail": avail
    })


def scrape():
    for url in url_dict:
        address = url_dict[url]
        add_address(address)
        add_building_data(address, url)


def write_csv():
    '''write data structure (in format in testing/data_structure.json) to a csv file'''


def create_csv_file():
    '''create a csv file for writing data'''


def main():
    '''
    '''
    get_url_list()
    scrape()
    print(data)


if __name__ == '__main__':
    main()
