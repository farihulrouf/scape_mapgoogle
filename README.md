# Google Maps Scraper

A Python script to scrape data from Google Maps using Selenium.

## Prerequisites

- Python 3.x
- pip

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate

   git clone https://github.com/farihulrouf/scrape_google_map.git
   cd scrape_google_map

   pip install -r requirements.txt
   
   cp .env.example .env  # Copy the example file
   MAX_CONCURRENT=6     # Recommended: Start with 100
   HEADLESS=False       # Set True for headless mode

   python3 scrape_map.py