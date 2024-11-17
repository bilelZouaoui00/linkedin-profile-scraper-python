import time
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from load_cookies import load_cookies

# Path to ChromeDriver
chrome_driver_path = r'C:/chromedriver-win64/chromedriver.exe'

# Perform scrolling to load dynamic content
def scroll_page(driver, total_scrolls=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(total_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached end of page.")
            break
        last_height = new_height

# Extract profile data
def extract_profiles(driver):
    time.sleep(5)  # Ensure the page is fully loaded
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    profiles = []

    # Find the list containing the profiles
    profiles_list = soup.find('ul', {'class': 'reusable-search__entity-result-list'})
    if not profiles_list:
        print("No profiles found. Check class names or dynamic content.")
        return profiles

    # Iterate over each profile in the list
    for li in profiles_list.find_all('li', {'class': 'reusable-search__result-container'}, recursive=False):
        try:
            # Extract profile URL (individual profile link)
            link_tag = li.find('a', {'class': 'app-aware-link'}, href=True)
            profile_url = link_tag['href'] if link_tag else None

            # Extract profile name
            name_tag = li.find('span', {'class': 'entity-result__title-text'})
            profile_name = name_tag.get_text(strip=True) if name_tag else None

            # Extract job title
            job_title_tag = li.find('div', {'class': 'entity-result__primary-subtitle'})
            job_title = job_title_tag.get_text(strip=True) if job_title_tag else None

            # Extract location
            location_tag = li.find('div', {'class': 'entity-result__secondary-subtitle'})
            location = location_tag.get_text(strip=True) if location_tag else None

            # Append the profile details to the list
            profiles.append({
                'url': profile_url,
                'name': profile_name,
                'job_title': job_title,
                'location': location
            })
        except Exception as e:
            print(f"Error extracting profile: {e}")

    return profiles


def main():
    # Initialize the driver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        # Load LinkedIn and cookies
        driver.get("https://www.linkedin.com")
        load_cookies(driver)
        driver.refresh()

        # Navigate to search results
        search_url = "https://www.linkedin.com/search/results/people/"
        driver.get(search_url)

        # Scroll and scrape profiles
        print("Scrolling...")
        scroll_page(driver)
        print("Scrolling complete. Extracting profiles...")
        profiles = extract_profiles(driver)

        # Save profiles to a JSON file
        with open('data/scraped_profiles.json', 'w') as file:
            json.dump(profiles, file)
        print(f"Extracted {len(profiles)} profiles.")
        print(profiles)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
