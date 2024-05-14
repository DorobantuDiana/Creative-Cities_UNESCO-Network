import pandas as pd
from datetime import datetime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from geopy.geocoders import Nominatim

def get_coordinates(city_name):
    """
    Retrieve latitude, longitude and country for a given city name.

    Args:
        city_name (str): Name of the city.

    Returns:
        tuple: latitude, longitude and country name (if found), otherwise (None, None, None).
    """
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(city_name, addressdetails=True)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        country = geolocator.reverse([latitude, longitude]).raw['address']['country']
        return latitude, longitude, country
    else:
        return None, None, None
    
path = '/Users/ddx/Documents/chromedriver-mac-arm64/chromedriver'
options = Options()
options.headless = True
options.add_argument("--headless=new")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
service = Service()
driver = webdriver.Chrome(service=service, options=options)



def scrape_page(url):
    """
    Scrape data from a single page of UNESCO Creative Cities website.

    Args:
        url (str): URL of the page to scrape.

    Returns:
        list: List of dictionaries containing scraped data for each city.
    """
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    city_section = soup.find('section', id='block-views-creative-cities-search-images')
    

    cities_data = []

    for city_item in city_section.find_all('div', class_='row-content'):
        city_name = city_item.find('h4', class_='title').text.strip()
        city_category = city_item.find('div', class_='category').text.strip()
        city_url = city_item.find('a')['href']

        latitude, longitude, country = get_coordinates(city_name)

        try:
            driver.get(city_url)
            city_soup = BeautifulSoup(driver.page_source, 'lxml')
            about_city = city_soup.find('div', class_='field-name-body').text.strip()
            added_value = city_soup.find('div', class_='field-name-field-added-value').text.strip()
            member_since = city_soup.find('div', class_='field-name-field-uncc-member-since-').find('span', class_='date-display-single').text.strip()

        except Exception as e:
            about_city = "Description not found"
            added_value = "Added value not found"
            member_since = "Member since not found"
       
        cities_data.append({
            'City Name': city_name,
            'Country': country,
            'Latitude': latitude,
            'Longitude': longitude,
            'City Category': city_category,
            'City URL': city_url,
            'About the Creative City': about_city,
            'Added Value': added_value,
            'Member since': member_since
        })

    
    return cities_data


def scrape_all_pages(base_url):
    """
    Scrape data from all pages of UNESCO Creative Cities website.

    Args:
        base_url (str): Base URL of the website.

    Returns:
        list: List of dictionaries containing scraped data for all cities.
    """
    all_cities_data = []
    page_num = 1
    continue_searching = True
    while continue_searching:
        url = f"{base_url}?page={page_num}"
        print(f'Current page: {page_num}')
        attempts = 0
        while True:
            try:
                page_data = scrape_page(url)
                if len(page_data) == 0:
                    continue_searching = False

                all_cities_data.extend(page_data)
                break

            except KeyboardInterrupt as e:
                raise e
            
            except:
                attempts += 1
                if attempts <= 100:
                    print('Found exception. Trying again.')
                    continue
                else:
                    continue_searching = False
                    break
        
        page_num += 1

    return all_cities_data


base_url = 'https://en.unesco.org/creative-cities/creative-cities-map'

# Scrape all pages of cities
all_cities_data = scrape_all_pages(base_url)

driver.quit()

# Convert the list of dictionaries to a DataFrame
cities_data_df = pd.DataFrame(all_cities_data)
current_date = datetime.now().strftime("%Y-%m-%d")
cities_data_df.to_json(f"./data/scrapped_cities_data_{current_date}.json")


