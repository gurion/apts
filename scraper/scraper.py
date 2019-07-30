import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import pandas

########## GLOBAL VARS #######################
BASE_URL = 'https://www.apartments.com/'
extension = 'new-york-ny/'  # This is your unique search identifier from a region
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
}
data = {'properties': {}}
##############################################


def get_url_list():
    '''return a list of property URLs to parse in a given polygon'''
    soup = get_page_soup(BASE_URL + extension)
    page_urls = get_all_page_urls(soup)
    listing_ids = []
    for url in page_urls:
        page = get_page_soup(url)
        listing_ids += get_property_ids_from_search_page(page)

    return listing_ids


def get_page_soup(url):
    '''get request a page and return beautiful soup object'''
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def get_all_page_urls(soup):
    '''Get all the urls needed to iterate over all the placards'''
    pages = soup.find('div', {'id': 'placardContainer'}).find('div', {'id': 'paging'}).find_all('a')
    start_page = pages[1].text
    last_page = pages[len(pages)-2].text
    return [BASE_URL+extension+str(page_number) for page_number in range(int(start_page), int(last_page) + 1)]


def get_property_ids_from_search_page(soup):
    '''get list of property listing IDs'''
    placards = soup.find('div', {'id': 'placardContainer'}).find_all('article', {})
    return [placard['data-listingid'] for placard in placards]


def get_property_address(soup):
    '''given page, extract address'''
    script = soup.find_all('script', type='text/javascript')[2].text
    address = find_tag(script, 'listingAddress') + ', ' + find_tag(script, 'listingCity') + \
        ', ' + find_tag(script, 'listingState') + ' ' + find_tag(script, 'listingZip')
    return address


def find_tag(text, tag):
    '''helper method for get_property_address'''
    tag = tag + ": \'"
    start = text.find(tag) + len(tag)
    end = text.find("\',", start)
    return str(text[start: end])


def get_building_data(url):
    '''Get the data from the table of apartments associated with the building'''
    soup = get_page_soup(url)
    address = get_property_address(soup)
    add_address(address)
    table_rows = soup.find('div', {'id': 'apartmentsTabContainer'}).find(
        'div', {'class': 'js-expandableContainer'}).find('tbody').find_all('tr')

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
    return float(baths)


def get_rent(tr):
    '''get rent'''
    rent = tr.find('td', {'class': 'rent'})
    if rent is None:
        return -1
    return int(rent.text.strip().replace(',', '').strip('$'))


def get_sqft(tr):
    '''get square footage'''
    sqft = tr.find('td', {'class': 'sqft'}).text
    if sqft == '':
        return -1
    return int(sqft.text.strip().replace(',', ''))


def get_avail(tr):
    '''get availability'''
    avail = tr.find('td', {'class': 'available'})
    if avail is None:
        return -1
    avail = 1 if avail.text == 'Available Now' else 0
    return avail


def add_address(address):
    '''add building to database'''
    data['properties'].update({
        address: {
            'units': [],
            'policies': {
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
    data["properties"][address]["units"].append({
        "unit": unit_num,
        "beds": beds,
        "baths": baths,
        "rent": rent,
        "sqft": sqft,
        "avail": avail
    })


def write_csv():
    '''write data structure (in format in testing/data_structure.json) to a csv file'''


def create_csv_file():
    '''create a csv file for writing data'''


def main():
    '''
    '''
    get_building_data("https://www.apartments.com/sky-new-york-ny/w1h7edh/")
    print(data)


if __name__ == '__main__':
    main()
