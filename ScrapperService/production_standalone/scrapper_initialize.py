# IMPORT UTILS
import re
import json
import time, os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

# VARIABLE
# ----------------------------------------------------
ENV = "PROD"
# ----------------------------------------------------
BASIC_PROD    = "." if ENV=="DEV" else "/Users/genereux/Documents/UM6P/COURS-S2/BI_KD/BankReviewIntelligence/ScrapperService/production_standalone"
CURRENT_DATE  = datetime.now().strftime("%Y-%m-%d")
CITIES_PATH   = BASIC_PROD + "/row_data/utils/countries_cities.json"
RAW_SAVE_PATH = BASIC_PROD + f"/row_data/temp/"
PARCKET_PATH  = BASIC_PROD + f"/row_data/parcket/{CURRENT_DATE}/"
# ----------------------------------------------------

# UTILS CLASS
class Utils:
    @staticmethod
    def is_phone_number(text):
        phone_pattern = re.compile(r"^\+?\d[\d\s-]{8,}\d$")
        return bool(phone_pattern.match(text))

    @staticmethod
    def is_website_url(text):
        url_pattern = re.compile(
            r'^(https?:\/\/)?'
            r'([\da-z\.-]+)\.'
            r'([a-z\.]{2,6})'
            r'([\/\w \.-]*)*\/?$'
        )
        return bool(url_pattern.match(text))

    @staticmethod
    def throw_error(e):
        print(f"Error: {e}")

    @staticmethod
    def load_cities(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
    @staticmethod
    def generate_google_maps_link(address):
        import urllib.parse
        base_url = "https://www.google.com/maps/search/?api=1&query="
        url_safe_address = urllib.parse.quote(address)
        return base_url + url_safe_address
    
    @staticmethod
    def delete_file(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

# CORE FUNCTION
def primary_search(browser):
    action = ActionChains(browser)
    a = browser.find_elements(By.CLASS_NAME, "hfpxzc")
    
    if not a:
        print("No elements found with class name 'hfpxzc'")
        return a, action
    
    last_len = len(a)
    same_len_count = 0
    
    while True:
        # Scroll down to the last element
        try:
            if not a:
                break
            scroll_origin = ScrollOrigin.from_element(a[-1])
            action.scroll_from_origin(scroll_origin, 0, 1000).perform()
            time.sleep(2)  # Wait for new results to load
          
            a = browser.find_elements(By.CLASS_NAME, "hfpxzc")
            
            if len(a) == last_len:
                same_len_count += 1
                if same_len_count > 5:
                    break
            else:
                last_len = len(a)
                same_len_count = 0
        except StaleElementReferenceException:
            print("StaleElementReferenceException occurred. Retrying...")
            continue
    return a, action
def extract_review(browser, action, verbose=False):
    # Click on "review button"
    try:
        tab_action = browser.find_elements(By.CLASS_NAME, "hh2c6")
        if tab_action == None or len(tab_action) < 2:
            return []
        advice_btn = tab_action[1]
        action.move_to_element(advice_btn).click().perform()
        time.sleep(2)
    except Exception as e:
        Utils.throw_error(e)

    # Scroll down until no more data is loading while loading reviews
    reviews_blocs = browser.find_elements(By.CLASS_NAME, "jJc9Ad") 
    last_reviews_count = len(reviews_blocs)
    if verbose:
        print(last_reviews_count)
    _same = 0
    while True:
        scroll_origin = ScrollOrigin.from_element(reviews_blocs[-1])
        action.scroll_from_origin(scroll_origin, 0, 1000).perform()
        time.sleep(2)
        reviews_blocs = browser.find_elements(By.CLASS_NAME, "jJc9Ad") 

        if len(reviews_blocs) == last_reviews_count:
            _same += 1
            if _same > 3:
                break
        else:
            last_reviews_count = len(reviews_blocs)
            _same = 0
        
    # Extract the reviews
    reviews = []
    for bloc in reviews_blocs:
        html_content = bloc.get_attribute('outerHTML')
        html_content = BeautifulSoup(html_content, 'html.parser')
        
        try:
            reviewer_name = html_content.find('div', {"class": "d4r55"}).text
            reviewer_star = len(html_content.findAll('span', {"class": "hCCjke google-symbols NhBTye elGi1d"}))
            reviewer_text = html_content.find('span', {"class": "wiI7pd"}).text if html_content.find('span', {"class": "wiI7pd"}) else "NAN"
            reviewer_publish_data = html_content.find('span', {"class": "rsqaWe"}).text
            reviewer_like_reaction = html_content.find('span', {"class": "pkWtMe"}).text if html_content.find('span', {"class": "pkWtMe"}) else 0
            reviewer_profil_link = html_content.find('button', {"class": "WEBjve"}).attrs.get('data-href')
            
            soup = html_content.findAll('div', {"class": "wiI7pd"})
            if soup != None or len(soup)!=0:
                chat = [msg.text for msg in soup]
                reviewer_owner_reply = "**".join(chat)
            else:
                reviewer_owner_reply = "NAN"

            soup = html_content.find('span', {"class": "DZSIDd"})
            reviewer_owner_reply_date = soup.text if soup else "NAN"

            reviews.append((reviewer_name, reviewer_star, reviewer_text, reviewer_publish_data, reviewer_like_reaction, reviewer_profil_link, reviewer_owner_reply, reviewer_owner_reply_date))
        except Exception as e:
            Utils.throw_error(e)
            continue
    return reviews
def extract(browser, sites, action, country, city, verbose=False):
    if not sites:
        print(f"No sites found for {city} in {country}")
        return

    full_review = None
    banks_name = []
    banks_info = []

    # Create temp file to store data
    columns=['Country', 'Town', 'Bank_Name', 'Bank_Phone_number', 'Bank_Address', 'Bank_Website', 'Reviewer_Nane', 'Reviewer_Sart', 'Reviewer_Text', 'Reviewer_Publish_Date', 'Reviewer_Like_Reaction', 'Reviewer_Profil_Link', 'Reviewer_Owner_Reply', 'Reviewer_Owner_Reply_Date']
    df = pd.DataFrame(columns=columns)
    temp_csv_path = os.path.join(RAW_SAVE_PATH, f"pull-{city}-{country}-{CURRENT_DATE}.csv")
    os.makedirs(os.path.dirname(temp_csv_path), exist_ok=True)
    df.to_csv(temp_csv_path, index=False, encoding='utf-8')

    # Treat ech sites
    for i in tqdm(range(len(sites))):
        try:
            if i>= len(sites):
                print(f"No more sites to preocess for {city} in {country}")
                break

            wait = WebDriverWait(browser, 2)
            wait.until(EC.element_to_be_clickable(sites[i]))
            scroll_origin = ScrollOrigin.from_element(sites[i])
            action.scroll_from_origin(scroll_origin, 0, 100).perform()
            action.move_to_element(sites[i]).perform()
            
            if sites[i] is not None:
                sites[i].click()
            time.sleep(2)
        except Exception as e:
            Utils.throw_error(e)
            print("StaleElementReferenceException occurred. Retrying...")
            #sites = primary_search(browser) 
            continue
        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        try:
            Name_Html = soup.findAll('h1', {"class": "DUwDvf lfPIob"})
            name = Name_Html[0].text
            if name not in banks_name:
                # Scrape Bank information
                banks_name.append(name)
                infos = soup.findAll('div', {"class": "Io6YTe"})
                phone = "Not available"
                for info in infos:
                    if Utils.is_phone_number(info.text):
                        phone = info.text
                address = infos[0].text if infos else "Not available"
                website = "Not available"
                for info in infos:
                    if Utils.is_website_url(info.text):
                        website = info.text
                if verbose:
                    print([name, phone, address, website])
                bank_details = (country, city, name, phone, address, website)
                
                # Scrape reviews
                reviews = extract_review(browser, action)
                for i in range(len(reviews)):
                    full_review = [bank_details + reviews[i]]

                # Save record
                df = pd.DataFrame(full_review, columns=columns)
                df['Reviewer_Like_Reaction'] = df['Reviewer_Like_Reaction'].astype(int)
                df.to_csv(temp_csv_path, mode='a', header=False, index=False, encoding='utf-8')
        except Exception as e:
            # Alert maintanier
            Utils.throw_error(e)
            continue
    
    # Save collected data into parcket
    directory = os.path.join(PARCKET_PATH, country)
    os.makedirs(directory, exist_ok=True)
    df = pd.read_csv(temp_csv_path)
    df.to_parquet(os.path.join(directory, f"{city}.parquet"), engine='pyarrow')
    Utils.delete_file(temp_csv_path)

# MAIN
def main():
    countries_cities = Utils.load_cities(CITIES_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--lang=fr")
    chrome_options.add_argument("--headless")
    
    for country, cities in countries_cities.items():
        print("PULLING: ", country)
        for city in tqdm(cities):
            browser = webdriver.Chrome(options=chrome_options)
            search_query = f"Banque {city}, {country} "
            browser.get(f"https://www.google.com/maps/search/{search_query}")
            time.sleep(10) 
            
            sites, action = primary_search(browser)
            extract(browser, sites, action, country, city)
            browser.quit()

if __name__ == "__main__":
    main()