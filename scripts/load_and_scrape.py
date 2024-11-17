import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup

# Path to ChromeDriver
chrome_driver_path = r'C:/chromedriver-win64/chromedriver.exe'

def scroll_page(driver):
    """Scroll to the bottom of the page to load dynamic content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_profiles(driver):
    """Extract profile information from the current page."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    profiles = []
    uls = soup.find('ul', {'class': 'reusable-search__entity-result-list'})
    if not uls:
        print("No profiles found on this page.")
        return profiles

    for li in uls.find_all('li', recursive=False):
        try:
            link = li.find('a', {'class': 'app-aware-link'})
            name = li.find('span', {'class': 'entity-result__title-text'}).get_text(strip=True)
            job_title = li.find('div', {'class': 'entity-result__primary-subtitle'}).get_text(strip=True)
            location = li.find('div', {'class': 'entity-result__secondary-subtitle'}).get_text(strip=True)

            if link:
                profile_url = link.get('href')
                profiles.append({
                    'url': profile_url,
                    'name': name,
                    'job_title': job_title,
                    'location': location
                })
        except AttributeError as e:
            print(f"Error extracting profile: {e}")
    return profiles

def navigate_pages_and_scrape(driver):
    """Paginate through the search results and scrape profiles."""
    all_profiles = []
    while True:
        scroll_page(driver)
        profiles = extract_profiles(driver)
        all_profiles.extend(profiles)
        print(f"Extracted {len(profiles)} profiles from this page.")
        
        # Check for the "Next" button and click it
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button.artdeco-pagination__button--next')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
            else:
                print("No more pages available.")
                break
        except (NoSuchElementException, ElementClickInterceptedException):
            print("Pagination ended or error occurred.")
            break

    return all_profiles

def navigate_pages_and_scrape(driver, max_profiles=100):
    """Paginate through the search results and scrape profiles."""
    all_profiles = []
    while len(all_profiles) < max_profiles:
        scroll_page(driver)
        profiles = extract_profiles(driver)
        all_profiles.extend(profiles[:max_profiles - len(all_profiles)])
        print(f"Total profiles scraped: {len(all_profiles)}")

        if len(all_profiles) >= max_profiles:
            break

        # Check for the "Next" button and click it
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button.artdeco-pagination__button--next')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
            else:
                print("No more pages available.")
                break
        except (NoSuchElementException, ElementClickInterceptedException):
            print("Pagination ended or error occurred.")
            break

    return all_profiles


def navigate_pages_and_scrape(driver, max_pages=10, max_profiles=200):
    """Paginate through the search results and scrape profiles."""
    all_profiles = []
    current_page = 0

    while current_page < max_pages and len(all_profiles) < max_profiles:
        scroll_page(driver)
        profiles = extract_profiles(driver)
        all_profiles.extend(profiles[:max_profiles - len(all_profiles)])
        print(f"Extracted {len(profiles)} profiles from page {current_page + 1}. Total: {len(all_profiles)}")
        current_page += 1

        if len(all_profiles) >= max_profiles:
            break

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button.artdeco-pagination__button--next')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(3)
            else:
                print("No more pages available.")
                break
        except (NoSuchElementException, ElementClickInterceptedException):
            print("Pagination ended or error occurred.")
            break

    return all_profiles

def main():
    # Initialize the driver
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.linkedin.com")
    
    # Load cookies
    with open('data/linkedin_cookies.json', 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()

    # Navigate to LinkedIn search results
    search_url = "https://www.linkedin.com/search/results/people/"
    driver.get(search_url)

    # Scrape profiles across pages
    # profiles = navigate_pages_and_scrape(driver)
    profiles = navigate_pages_and_scrape(driver, max_pages=5, max_profiles=50)


    # Save results to JSON
    with open('data/scraped_profiles.json', 'w', encoding='utf-8') as file:
        json.dump(profiles, file, indent=4, ensure_ascii=False)

    print(f"Total profiles scraped: {len(profiles)}")
    driver.quit()

if __name__ == "__main__":
    main()
