# Import libraries and packages for the project
import json
import random
import re
import time
from time import sleep

from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

import csv
import urllib.parse

from selenium.webdriver.support.wait import WebDriverWait

print('- Finish importing packages')

# Task 1.1: Open Chrome and Access LinkedIn login site
#options = webdriver.ChromeOptions()
#options = webdriver.ChromeOptions()
#options.add_argument("--headless")
#options.add_experimental_option("detach", True)
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

#driver = webdriver.Chrome()
#driver = webdriver.Chrome(options=options)

##############################
# using chromedriver
chrome_driver_path = 'C:/chromedriver-win64/chromedriver.exe'
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
"""options.add_argument('--window-size=1920x1080')
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")"""

driver = webdriver.Chrome(service=service, options=options)
sleep(2)
url = 'https://www.linkedin.com/login'
driver.get(url)
print('- Finish initializing a driver')
sleep(2)

try :
    # Task 1.2: Import username and password
    credential = open('credentials.txt')
    line = credential.readlines()
    username = line[0]
    password = line[1]
    print('- Finish importing the login credentials')
    sleep(2)

    # Task 1.2: Key in login credentials
    email_field = driver.find_element(By.ID, 'username')
    email_field.send_keys(username)
    print('- Finish keying in email')
    sleep(3)

    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(password)
    print('- Finish keying in password')
    sleep(2)

    # Task 1.2: Click the Login button
    signin_field = driver.find_element(By.XPATH, '//button[@type="submit"]')
    signin_field.click()

    WebDriverWait(driver, 10).until(EC.url_contains('https://www.linkedin.com/feed/'))
    cookies = driver.get_cookies()
    driver.quit()

    # password_field.submit()
    # Locate and click the 'Sign in' button
    # sign_in_button = (WebDriverWait(driver, 10)
    # .until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))))
    # sign_in_button.click()
    sleep(3)

    print('- Finish Task 1: Login to Linkedin')

    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://www.linkedin.com')

    for cookie in cookies:
        driver.add_cookie(cookie)

    # Define the base LinkedIn URL and query parameters
    base_url = "https://www.linkedin.com/search/results/people/"

    # Query parameters
    industries = ["Software Development", "Information Technology & Services", "Telecommunications",
                  ""]  # Example industry codes as strings
    job_titles = ["Directeur des Partenariats", "Chef de Produit", "Responsable Marketing", "HR manager"]
    keywords = "hr manager"
    origin = "FACETED_SEARCH"
    sid = "g4*"

    # Encode the list of industries as a JSON array and URL encode the entire query string
    query_params = {
        "industry": urllib.parse.quote(f'[{",".join([f"{industry}" for industry in industries])}]'),
        "keywords": keywords,
        "origin": origin,
        "sid": sid
    }

    # Combine base URL with the encoded query parameters
    url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
    driver.get(url)

    total_scrolls = 5
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(total_scrolls):
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script(f'window.scrollTo(0, {scroll_height});')

        # Random delay between scrolls
        time.sleep(random.uniform(3, 6))

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml')
    uls = soup.find('ul', {'class': 'display-flex list-style-none flex-wrap'})

    if uls is None:
        print("Could not find 'ul' element with class 'display-flex list-style-none flex-wrap'")
        # redis_conn.set('scraped_data', json.dumps([]))
    else:
        pr = []
        for li in uls.findAll('li'):
            try:
                r = li.find('a', {'class': 'app-aware-link'}).get('href')
                parsed_url = urllib.urlparse(r)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

                pr.append(r)
            except Exception as e:
                print(f"Error processing 'li' element: {e}")

        random.shuffle(pr)  # Randomize the order of profiles before scraping
        print(f"len(out): {len(pr)}")
        out = []
        new_people_count = 0
        for c, p in enumerate(pr):
            try:
                driver.get(p)
                time.sleep(8)
                src = driver.page_source
                soup = BeautifulSoup(src, 'lxml')
                url = p
                name = soup.find('h1', {
                    'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'}).get_text().strip()

                title = soup.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
                location = soup.find('span', {
                    'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
                dets = soup.find_all('div', {'class': 'inline-show-more-text--is-collapsed'})
                company_name = dets[0].get_text().strip() if dets else ''
                img_tag = soup.find('img', {
                    'class': 'presence-entity__image EntityPhoto-circle-1 evi-image lazy-image ember-view'})
                img_url = img_tag['src'] if img_tag else ''
                names = name.split(" ", 1)
                first_name = names[0].lower() if names else ''
                last_name = names[1].lower() if names else ''
                first_name = re.sub(r"\s+", "", first_name, flags=re.UNICODE)
                last_name = re.sub(r"\s+", "", last_name, flags=re.UNICODE)
                person = {"url": url, "name": name, "title": title, "location": location,
                      "company": company_name, "img_url": img_url}

                out.append(person)
                print(f"Scraped data for {name}: {person}")
                progress_step = len(out)
                progress_percent = (progress_step / st_num) * 100

                new_people_count += 1

                if new_people_count >= st_num:
                   break  # Stop when we've added the required number of new people
                print(progress_percent)
            except Exception as e:
                 print(f"Error scraping profile {p}: {e}")
    print(pr)
    print(out)






except Exception as e:
      print(f"An error occurred during the scraping process: {e}")


finally :
  driver.quit()

#url = 'https://www.linkedin.com/search/results/people/?keywords=hr%20manager&origin=SWITCH_SEARCH_VERTICAL&sid=Wg!'
#url1 = 'https://www.linkedin.com/search/results/people/?industry=%5B%226%22%2C%224%22%5D&keywords=hr%20manager&origin=FACETED_SEARCH&sid=g4*'

# Task 2: Search for the profile we want to crawl
# Wait for the search field to load, then access it
#search_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"]')))

""" # Apply industry filter (optional)
    if industry_filter:
        industry_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Industry")]'))
        )
        industry_button.click()
        industry_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[contains(@placeholder, "Add an industry")]'))
        )
        industry_input.send_keys(industry_filter)
        industry_input.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for the filter to apply

    print("Search with filters applied successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver if needed
    driver.quit()"""


"""search_field = driver.find_element(By.XPATH, "//input[@aria-label='Search']")
print('- Finish Task 2: Search for profilesf')
# Enter a search query (e.g., 'Tech Companies')
search_field.send_keys("HR Manager")

# Press Enter to initiate the search
search_field.send_keys(Keys.RETURN)

print("Search executed successfully!")

# Task 2.1: Locate the search bar element
#search_field = driver.find_element(By.CLASS_NAME, "input.search-global-typeahead__input")

# Task 2.2: Input the search query to the search bar
#search_query = input('What Tech Companies do you want to scrape? ')
#search_field.send_keys(search_query)

# Task 2.3: Search
#search_field.send_keys(Keys.RETURN)

print('- Finish Task 2: Search for profiles')"""


# Task 3: Scrape the URLs of the profiles

# Task 3.1: Write a function to extract the URLs of one page
"""def GetURL():
    page_source = BeautifulSoup(driver.page_source, "html.parser")
    profiles = page_source.find_all('a', class_='app-aware-link ')
    all_profile_URL = []
    for profile in profiles:
        profile_ID = profile.get('href')

        profile_URL = "https://www.linkedin.com/in/" + profile_ID
        if profile_URL not in all_profile_URL:
            all_profile_URL.append(profile_URL)
    return all_profile_URL"""

#links = soup.find_all('a')
#urls = [link.get('href') for link in links]
#print(urls)



# Task 3.2: Navigate through many page, and extract the profile URLs of each page

"""input_page = int(input('How many pages you want to scrape: '))
URLs_all_page = []
for page in range(input_page):
    URLs_one_page = GetURL()
    sleep(2)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')  #scroll to the end of the page
    sleep(3)
    next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
    driver.execute_script("arguments[0].click();", next_button)
    URLs_all_page.append(URLs_one_page)
    sleep(2)

print('- Finish Task 3: Scrape the URLs')"""





# Task 4: Scrape the data of 1 Linkedin profile, and write the data to a .CSV file

#"""with open('output.csv', 'w',  newline = '') as file_output:
""" headers = ['Name', 'Job Title', 'Location', 'LinkedInURL', 'Company', 'CompanyURL']
    writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n',fieldnames=headers)
    writer.writeheader()
    for linkedin_URL in URLs_all_page:
        driver.get(linkedin_URL)
        print('- Accessing profile: ', linkedin_URL)

        page_source = BeautifulSoup(driver.page_source, "html.parser")

        info_div = page_source.find('div',{'class':'flex-1 mr5'})
        info_loc = info_div.find_all('ul')
        name = info_loc[0].find('li').get_text().strip() #Remove unnecessary characters
        print('--- Profile name is: ', name)
        location = info_loc[1].find('li').get_text().strip() #Remove unnecessary characters
        print('--- Profile location is: ', location)
        title = info_div.find('h2').get_text().strip()
        print('--- Profile title is: ', title)
        writer.writerow({headers[0]:name, headers[1]:location, headers[2]:title, headers[3]:linkedin_URL})
        print('\n')

print('Mission Completed!')"""