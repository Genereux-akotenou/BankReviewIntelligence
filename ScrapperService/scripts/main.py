import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .scraper import primary_search, extract
from .utils import Utils
import config

def main():
    countries_cities = Utils.load_cities(config.CITIES_PATH)
    
    chrome_options = Options()
    chrome_options.add_argument("--lang=fr")
    #chrome_options.add_argument("--headless")

    for country, cities in countries_cities.items():
        for city in cities:
            browser = webdriver.Chrome(options=chrome_options)
            search_query = f"{country} Bank {city}"
            browser.get(f"https://www.google.com/maps/search/{search_query}")
            time.sleep(10) 
            
            sites, action = primary_search(browser)
            extract(browser, sites, action, country, city)
            browser.quit()

if __name__ == "__main__":
    main()
