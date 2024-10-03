'''
This script is designed to scrape information from UNESCO "Creative Cities" Network (UCCN) webpage 
using the <Selenium> web driver and <BeautifulSoup> for HTML parsing. 
It extracts data about different cities, such as their name category and description, 
then stores it in a JSON file for further analysis. 
The data is gathered from multiple paginated web pages and saved as a structured dataset using pandas DataFrame.
'''

import pandas as pd

from datetime import datetime
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up webdriver (e.g.: chromedriver(Google Chrome), geckodriver(Firefox)) 
path = './chromedriver-mac-arm64/chromedriver' # path to webdriver
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


def get_city_links(base_url):
    '''
    Scrape the city links from all pages of UNESCO Creative Cities website.

    Args:
        base_url: Base URL of the website.

    Returns:
        list: List of website links.
    '''
    page_num = 0
    links_list =[]

    while True:
        url = f"{base_url}{page_num}"
        print(f'Current page: {page_num}')

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'lxml')

        cities = soup.find_all('div', class_='col-12 col-md-6 col-lg-4 col-xl-3')

        if not cities:
            print('No more pages found.')
            break

        for city in cities:
            link = city.a['href']
            links_list.append(link)

        page_num += 1

    return links_list

    
def scrape_page(url):
    '''
    Scrape data from a single page of UNESCO Creative Cities website.

    Args:
        url (str): URL of the page to scrape.

    Returns:
        list: List of dictionaries containing scraped data for each city.
    '''

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    city_data = []

    continue_searching = True
    while continue_searching:
        attempts = 0
        while True:
            try:
                city_name = soup.find('div', class_='pl-0 ml-0').text.strip()
                city_category = soup.find('div', class_='pb-2').a.text.strip()
                city_description = soup.find('div', class_='pl-0 cce001--description').text.strip()
                continue_searching = False
                break
            
            except:
                attempts+=1
                time.sleep(5)
                if attempts <= 100:
                    print('Found exception. Trying again.')
                    continue
                else:
                    city_name = "City name not found"
                    city_category = "City category not found"
                    city_description = "City description not found"
                    continue_searching = False
                    break

    city_data.append({
        'City Name': city_name,
        'Category': city_category,
        'Description': city_description,
        'Link': url
    })

    return city_data




base_url = "https://www.unesco.org/en/creative-cities/grid?f%5B0%5D=dataset_filters%3Ab64fd24b-e80d-4393-a62e-50ae79e696f3&hub=80094&page="

# Get all the city links
links = get_city_links(base_url)

# Scrape all pages of cities
all_cities_data = []
for link in links:
    print(f'Scraping {link}')
    city_data = scrape_page(link)
    all_cities_data.append(city_data)


# Close the browser
driver.quit()


# Convert the list of dictionaries to a DataFrame
cities_data_df = pd.DataFrame(all_cities_data)
current_date = datetime.now().strftime("%Y-%m-%d")
cities_data_df.to_json(f"./data/scrapped_cities_data_{current_date}.json")































