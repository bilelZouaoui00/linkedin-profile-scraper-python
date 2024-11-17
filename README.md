# LinkedIn Profile Scraper Python

**LinkedIn Profile Scraper Python** is a web scraping project built with Selenium and Python to extract profile data from LinkedIn search results. The scraper automates the login process using saved cookies, navigates through LinkedIn pages, and collects information such as profile URLs, names, job titles, and locations.

## Features

- **Automated Login:** Uses saved cookies to log in, bypassing the need for manual login each time.
- **Profile Scraping:** Extracts data like:
  - Profile URLs
  - Names
  - Job Titles
  - Locations
- **Efficient Pagination:** Scrolls through pages and collects results dynamically.
- **JSON Output:** Stores scraped data in a JSON file (`scraped_profiles.json`).

## Project Structure

linkedin-profile-scraper-python/
├── scripts/               # Python scripts for scraping
│   ├── save_cookies.py    # Save LinkedIn cookies to a JSON file
│   ├── load_cookies.py    # Load cookies and authenticate session
│   ├── load_and_scrape.py # Scrape LinkedIn profiles using cookies
├── data/                  # Directory for storing data
│   ├── linkedin_cookies.json   # Stored session cookies (ignored by Git)
│   ├── scraped_profiles.json   # Scraped LinkedIn profile data (ignored by Git)
├── .gitignore             # Ignored files (JSON data, virtual environment, etc.)
├── README.md              # Project description and instructions
├── requirements.txt       # Dependencies for the project
└── venv/                  # Python virtual environment (ignored by Git)


# Setup
## Prerequisites
1. Python 3.8+ installed on your system
2. Google Chrome and Chromedriver installed
3. A LinkedIn account

## Installation
# Step 1: Clone the repository
git clone https://github.com/username/linkedin-profile-scraper-python.git
cd linkedin-profile-scraper-python

# Step 2: Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt
  