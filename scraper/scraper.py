import requests
from bs4 import BeautifulSoup
import csv
import json
import re
from tqdm import tqdm

################################################################################
# Global Vars
################################################################################


BASE_URL = 'https://www.apartments.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0'
}
data = {}
url_dict = {}
errors = {}

################################################################################
# Getting URLs and page data
################################################################################


def fill_url_dict(extension):
    '''return a list of property URLs to parse in a given polygon'''
    soup = get_page_soup(BASE_URL + extension)
    page_urls = get_all_page_urls(extension, soup)
    for url in tqdm(page_urls):
        get_property_addresses_and_urls_from_search_page(get_page_soup(url))


def get_page_soup(url):
    '''get request a page and return beautiful soup object'''
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def get_all_page_urls(extension, soup):
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
    try:
        street = property['Address']['streetAddress']
    except:
        street = 'STREET'
    try:
        city = property['Address']['addressLocality']
    except:
        city = 'CITY'
    try:
        state = property['Address']['addressRegion']
    except:
        state = 'STATE'
    try:
        zip_code = property['Address']['postalCode']
    except:
        zip_code = '#####'
    return street + ', ' + city + ', ' + state + ' ' + zip_code


def add_building_data(address, url):
    '''Get the data from the table of apartments associated with the building'''
    soup = get_page_soup(url)
    pets, parking, built, renovated, num_units, stories, fitness, outdoor = get_amenity_info(
        soup)
    add_building_policies(address, pets, parking, built,
                          renovated, num_units, stories, fitness, outdoor)
    table_rows = []
    try:
        table_rows = soup.find('div', {'id': 'apartmentsTabContainer'}).find(
            'div', {'class': 'js-expandableContainer'}).find('tbody').find_all('tr')
    except:
        try:
            table_rows = soup.find('section', {'id': 'availabilitySection'}).find(
                'tbody').find_all('tr', {'class': 'rentalGridRow'})
        except Exception as e:
            errors.update({e: url})

    for tr in table_rows:
        parse_row(tr, url)


################################################################################
# Getting data for an individual apartment
################################################################################


def parse_row(row, url):
    '''get relevant data from a table row'''
    try:
        add_unit(url_dict[url], get_unit_name(row), get_beds(row),
                 get_baths(row), get_rent(row), get_sqft(row), get_avail(row))
    except Exception as e:
        errors.update({e: url})


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
    rent = tr.find('td', {'class': 'rent'}).text.strip()
    rent = re.sub('[^0-9\-]', '', rent)
    if rent == '':
        return -1
    try:
        return int(rent)
    except:
        range = rent.split('-')
        return int((int(range[0]) + int(range[1]))/2)


def get_sqft(tr):
    '''get square footage'''
    sqft = tr.find('td', {'class': 'sqft'}).text.strip()
    if (sqft == '' or sqft == '-'):
        return -1
    return int(sqft.split()[0].strip().replace(',', ''))


def get_avail(tr):
    '''get availability'''
    avail = tr.find('td', {'class': 'available'}).get_text().strip()
    if avail == 'Available Now':
        return 1
    else:
        return 0

################################################################################
# Getting Amenity Info
################################################################################


def get_amenity_info(soup):
    '''get building amenity info from page'''
    pets = get_pet_info(soup)
    parking = get_parking_info(soup)
    built, renovated, num_units, stories = get_building_info(soup)
    fitness = get_fitness_info(soup)
    outdoor = get_outdoor_info(soup)
    return pets, parking, built, renovated, num_units, stories, fitness, outdoor


def get_pet_info(soup):
    '''get building pet policy'''
    try:
        policies = soup.find_all('div', {'class': 'petPolicyDetails'})
        return ';'.join([policy.find('span').text.strip() for policy in policies])
    except Exception as e:
        return 'N/A'


def get_parking_info(soup):
    '''get parking info for a building'''
    try:
        policies = soup.find_all('div', {'class': 'parkingTypeFeeContainer'})
        return ';'.join([policy.text.strip() for policy in policies])
    except Exception as e:
        return 'N/A'


def get_building_info(soup):
    '''get building build/reno date and num units'''
    try:
        building_info = {
            'Built': 'N/A',
            'Renovated': 'N/A',
            'Units': 'N/A',
            'Stories': 'N/A'
        }
        info = soup.find('div', {'class': 'propertyFeatures'}).find_all('li')
        for li in info:
            li = li.text.strip().replace('•', '')
            add_to_building_info(building_info, li)
        return building_info["Built"], building_info["Renovated"], building_info["Units"], building_info["Stories"]

    except Exception as e:
        return 'N/A', 'N/A', 'N/A', 'N/A'


def add_to_building_info(dict, li):
    '''helper for get_building_info'''
    if 'Built' in li:
        li = re.sub('[^0-9]', '', li)
        dict['Built'] = li
    elif 'Renovated' in li:
        li = re.sub('[^0-9]', '', li)
        dict['Renovated'] = li
    else:
        li = li.split('/')
        dict['Units'] = re.sub('[^0-9]', '', li[0])
        dict['Stories'] = re.sub('[^0-9]', '', li[1])


def get_fitness_info(soup):
    '''get info associated with fitness centers etc'''
    try:
        fitness = soup.find('i', {'class': 'fitnessIcon'}
                            ).parent.parent.find_all('li')
        return ';'.join([li.text.replace('•', '') for li in fitness])
    except:
        return 'N/A'


def get_outdoor_info(soup):
    try:
        outdoor = soup.find('i', {'class': 'parksIcon'}
                            ).parent.parent.find_all('li')
        return ';'.join([li.text.replace('•', '') for li in outdoor])
    except:
        return 'N/A'


################################################################################
# Appending to dicts
################################################################################


def add_address(address):
    '''add building to database'''
    data.update({
        address: {
            'units': [],
            'policies': {}
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


def add_building_policies(address, pets, parking, built, renovated, num_units, stories, fitness, outdoor):
    '''Add amenity info for a given address'''
    data[address]['policies'].update({
        'pets': pets,
        'parking': parking,
        'built': built,
        'renovated': renovated,
        'num_units': num_units,
        'stories': stories,
        'fitness': fitness,
        'outdoor': outdoor
    })


################################################################################
# Big picture
################################################################################


def scrape():
    '''get data for all apartments from each url'''
    for url in tqdm(url_dict):
        address = url_dict[url]
        add_address(address)
        add_building_data(address, url)


def write_csv():
    '''write data to a csv file'''
    with open('apts.csv', mode='w') as file:
        fields = ['address', 'unit', 'beds', 'baths', 'rent', 'sqft', 'avail', 'pets',
                  'parking', 'built', 'renovated', 'num_units', 'stories', 'fitness', 'outdoor']
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()
        for address in tqdm(data):
            for unit in data[address]['units']:
                unit.update(data[address]['policies'])
                writer.writerow(unit)


################################################################################
# Main
################################################################################
def test():
    '''testing minor stuff as I go'''
    pass


def main():
    '''find all the urls, scrape the data, write to csv'''

    extension = input('Please enter your unique search ID:\n') + '/'

    print('Getting all property URLs...')
    fill_url_dict(extension)

    print('Getting property data...')
    scrape()

    print('Writing CSV...')
    write_csv()

    if errors != {}:
        print('Some errors occurred:\n')
        for error in errors:
            print('\t', error, ':', errors[error])


if __name__ == '__main__':
    main()
