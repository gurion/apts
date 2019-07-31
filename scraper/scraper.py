import requests
from bs4 import BeautifulSoup
import csv
import json
import re
import pandas

########## GLOBAL VARS #######################
BASE_URL = 'https://www.apartments.com/'
# This is your unique search identifier from a region
extension = '?sk=2e9f24608a4a19df461e27d9e96015fa&bb=ioh107pkwH_m-0yC/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
}
data = {}
url_dict = {}
##############################################


def fill_url_dict():
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
        try:
            table_rows = soup.find('section', {'id': 'availabilitySection'}).find(
                'tbody').find_all('tr', {'class': 'rentalGridRow'})
        except:
            print(url)
    for tr in table_rows:
        try:
            unit = get_unit_name(tr)
            beds = get_beds(tr)
            baths = get_baths(tr)
            rent = get_rent(tr)
            sqft = get_sqft(tr)
            avail = get_avail(tr)
            add_unit(address, unit, beds, baths, rent, sqft, avail)
        except:
            print(url)


def get_unit_name(tr):
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
    sqft = tr.find('td', {'class': 'sqft'}).text.strip()
    if (sqft == '' or sqft == '-'):
        return -1
    return int(sqft.split()[0].strip().replace(',', ''))


def get_avail(tr):
    '''get availability'''
    avail = tr.find('td', {'class': 'available'})
    if avail is None:
        return -1
    if avail.get_text() == 'Available Now':
        return 1
    else:
        return 0


def add_address(address):
    '''add building to database'''
    data.update({
        address: {
            'units': [],
            'policies': {
                'pets': 'TBD',
                'parking': 'TBD',
                'property_info': 'TBD',
                'fitness': 'TBD',
                'outdoor': 'TBD'
            }
        }
    })


def add_unit(address, unit_num, beds, baths, rent, sqft, avail):
    '''add a unit to the database'''
    data[address]['units'].append({
        'address': address,
        'unit': unit_num,
        'beds': beds,
        'baths': baths,
        'rent': rent,
        'sqft': sqft,
        'avail': avail
    })


def scrape():
	'''get data for all apartments from each url'''
    for url in url_dict:
        address = url_dict[url]
        add_address(address)
        add_building_data(address, url)


def write_csv():
    '''write data to a csv file'''
    with open('apts.csv', mode='w') as file:
        fields = ['address', 'unit', 'beds', 'baths', 'rent', 'sqft', 'avail']
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()
        for address in data:
            for unit in data[address]['units']:
                writer.writerow(unit)


def main():
    '''find all the urls, scrape the data, write to csv'''
    fill_url_dict()
    scrape()
    write_csv()


if __name__ == '__main__':
    main()
