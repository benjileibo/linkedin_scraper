# pip3 install --user linkedin_scraper
# pip install webdriver-manager

import gspread
import datetime
from faker import Faker
from faker.providers.person.en import Provider
from linkedin_scraper import Person, actions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pandas as pd
import re
import time 

# Parameters
spreadsheet_id = '1F4CZql8SwOAcyd334vnkiiJPsNygGQ8SZp8KsV09URY'

# Get next available row
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list)+1)

# Pull linkedin credentials
creds = pd.read_csv('../creds.csv')
email = creds.loc[creds.key == 'username',"value"].values[0]
password = creds.loc[creds.key == 'password',"value"].values[0]

gc = gspread.service_account(filename='/Users/benleibowitz/Downloads/trusty-sentinel-348204-ef2d96a570ec.json')
sh = gc.open_by_key(spreadsheet_id).sheet1
last_row = int(next_available_row(sh))

# Login to LinkedIn
driver = webdriver.Chrome(ChromeDriverManager().install())
actions.login(driver, email, password)

# Search for keyword
keywords = ["stealth biotech founder"]
wait_time = 2

for keyword in keywords:
    
    time.sleep(wait_time)
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/input').send_keys(keyword)
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/input').send_keys(Keys.RETURN)
    time.sleep(wait_time)

    expand_url = re.findall('https://(.*?)CLUSTER_EXPANSION', driver.page_source)[0] + "CLUSTER_EXPANSION"
    driver.get("http://" + expand_url)

    while True:

        # Scroll to bottom
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(wait_time)  
        
        # # Get only the unqiue profiles of interest
        html = driver.page_source
        profiles = re.findall('https://www.linkedin.com/in/.*?(?=\?miniProfile)', driver.page_source)
        
        for profile in profiles: 
            if profiles.count(profile) < 2: 
                profiles.remove(profile)

        # Remove duplicate profiles
        profiles = list(set(profiles))
        gsheet_profiles = sh.col_values(1)
        profiles = [profile for profile in profiles if profile not in gsheet_profiles]
        
        # Update google sheet with latest round of profiles
        for profile in profiles:
            sh.update(f'A{last_row}', profile)
            sh.update(f'B{last_row}', str(datetime.datetime.now()))
            last_row += 1
            time.sleep(wait_time)

        
        try:
            # Scroll to bottom
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(wait_time) 

            # Find next page button then click it
            str_index = re.search('aria-label="Next" id="ember', driver.page_source).end()
            ember = int(driver.page_source[str_index:str_index+3])
            driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
            time.sleep(wait_time)
        except:
            # Scroll to bottom
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(wait_time) 

            try:
                # Scroll to bottom
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                time.sleep(wait_time) 

                # Find next page button then click it (ember length = 3)
                str_index = re.search('aria-label="Next" id="ember', driver.page_source).end()
                ember = int(driver.page_source[str_index:str_index+3])
                driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
                time.sleep(wait_time)
                continue
            except:
                try:
                    # Scroll to bottom
                    html = driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    time.sleep(wait_time) 

                    # Find next page button then click it (ember length = 4)
                    ember = int(driver.page_source[str_index:str_index+4])
                    driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
                    time.sleep(wait_time)
                    continue
                except:
                    # Scroll to bottom
                    html = driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    time.sleep(wait_time) 
                    continue

