import json
from selenium import webdriver

# Load cookies from file
def load_cookies(driver, file_path='linkedin_cookies.json'):
    try:
        with open(file_path, 'r') as file:
            cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies loaded successfully.")
    except FileNotFoundError:
        print("No cookies file found. Please run save_cookies.py first.")
