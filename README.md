# Google Maps Scraper

A Python script to scrape data from Google Maps using Playwright.

## Prerequisites

- Python 3.x
- pip

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate


## Clone fro git
2. **Clone git repo**:
   ``bash
   git clone https://github.com/farihulrouf/scrape_google_map.git
   cd scrape_google_map

## Install dependency 
3. **install**:
   ```bash
   pip install -r requirements.txt

## Setting .env
4. **setting .env**:
   ```bash
   cp .env.example .env  # Copy the example file
   MAX_CONCURRENT=6     # Recommended: Start with 100
   HEADLESS=True         #if you choose False browser will appear  



## Run Program .env
5. **Running**:
   if you dont have file, Please download file csv LINKS.csv here www](https://drive.google.com/file/d/1nozcf5TH0xDfkp-3cv0DKg4amwKCGRfK/view?usp=sharing.
   place file Links.csv to this folder
   running program with script
   ```bash
   python3 scrape_map.py
