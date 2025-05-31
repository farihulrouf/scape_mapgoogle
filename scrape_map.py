import csv
import asyncio
from playwright.async_api import async_playwright
import re
import os
from tqdm.asyncio import tqdm
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
load_dotenv()
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", 5))  # default 5 kalau tidak ada

HEADLESS = os.getenv("HEADLESS", "True").lower() in ("true", "1", "yes")
# Output file CSV
CSV_OUTPUT_FILE = "result_scraping.csv"

# Cek apakah file sudah ada, kalau belum buat header
if not os.path.exists(CSV_OUTPUT_FILE):
    with open(CSV_OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["No", "Business Name", "Business Category", "Address", "Phone Number", "Email", "Website URL"])

def get_starting_row_number():
    try:
        with open(CSV_OUTPUT_FILE, mode='r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 1

row_counter = get_starting_row_number()

def clean_website_url(url):
    return re.sub(r'[^\x20-\x7E]+', '', url).strip()

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

async def scrape_google_maps(url, semaphore):
    global row_counter
    if not is_valid_url(url):
        print(f"❌ Skip invalid URL: {url}")
        return

    async with semaphore:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=HEADLESS)
                context = await browser.new_context()
                page = await context.new_page()

                print(f"🌐 Open URL: {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_selector('h1.DUwDvf', timeout=30000)

                name = await page.locator('h1.DUwDvf').inner_text()

                # Cari kategori berdasarkan jsaction (versi 17 dan 100)
                category_selectors = [
                    'button[jsaction="pane.wfvdle17.category"]',
                    'button[jsaction="pane.wfvdle100.category"]'
                ]
                category = "Kategori Not Found"
                for selector in category_selectors:
                    try:
                        category = await page.locator(selector).first.inner_text()
                        if category:
                            break
                    except:
                        continue

                try:
                    full_text = await page.locator('div[role="main"]').inner_text()
                    address_match = re.search(r"\n(.+?)(?=\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\Z)", full_text, re.DOTALL)
                    address = address_match.group(1).strip() if address_match else "Alamat Not Found"
                except:
                    address = "Alamat Not Found"

                try:
                    website = await page.locator('div.RcCsl.fVHpi.w4vB1d.NOE9ve.M0S7ae.AG25L a').get_attribute('href')
                    if website:
                        website = clean_website_url(website).replace('http://', '').replace('https://', '')
                    else:
                        website = "Website Not Found"
                except:
                    try:
                        website = await page.locator('[data-item-id="authority"]').inner_text()
                        website = clean_website_url(website) if website else "Website Not Found"
                    except:
                        website = "Website Not Found"

                phone = "Nomor telepon Not Found"
                try:
                    phone_candidates = await page.locator('div.Io6YTe.fontBodyMedium.kR99db').all_inner_texts()
                    for text in phone_candidates:
                        if re.search(r"\+?\d[\d\s\-\(\)]{7,}", text):
                            phone = text
                            break
                except:
                    pass

                email = "Email Not Found"
                try:
                    full_page_text = await page.locator("body").inner_text()
                    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_page_text)
                    if emails:
                        email = emails[0]
                except:
                    pass

                with open(CSV_OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        row_counter,
                        name,
                        category,
                        address,
                        phone,
                        email,
                        website
                    ])
                    row_counter += 1

                print("\n✅ Data scraping:")
                print(f"Business Name    : {name}")
                print(f"Business Category: {category}")
                print(f"Address          : {address}")
                print(f"Phone Number     : {phone}")
                print(f"Email Address    : {email}")
                print(f"Website URL      : {website}\n")

                await browser.close()

        except Exception as e:
            print(f"❌ Error saat scrape {url}: {e}")

def read_urls_from_csv(csv_path, link_count_target):
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Link Count'] == str(link_count_target):
                for key, value in row.items():
                    if key != 'Link Count' and value.strip() and is_valid_url(value.strip()):
                        urls.append(value.strip())
                break
    return urls

async def process_batch(csv_file, link_count_target, max_concurrent=MAX_CONCURRENT):
    start_time = time.perf_counter()
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n🚀 Mulai batch Link Count = {link_count_target} pada {start_datetime}")
    urls = read_urls_from_csv(csv_file, link_count_target)
    print(f"Jumlah URL: {len(urls)}")

    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [scrape_google_maps(url, semaphore) for url in urls]

    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Scraping batch {link_count_target}"):
        await f

    end_time = time.perf_counter()
    duration = timedelta(seconds=round(end_time - start_time))
    print(f"✅ Selesai batch Link Count = {link_count_target}")
    print(f"⏱️ Durasi: {duration}\n")

async def main():
    csv_file = 'Links.csv'

    # Baca semua baris Link Count secara berurutan
    link_counts = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                count = int(row['Link Count'])
                link_counts.append(count)
            except ValueError:
                continue

    # Jalankan scraping batch berdasarkan urutan baris
    for link_count in link_counts:
        await process_batch(csv_file, link_count)

if __name__ == '__main__':
    asyncio.run(main())
