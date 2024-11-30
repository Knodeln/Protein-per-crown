from bs4 import BeautifulSoup
from selenium import webdriver
import time
from database.connection import Connection
import re

all_products_start_time = time.time()

all_products_urls = []

with open("willys_urls.txt") as url_file:
    for url in url_file:

        driver = webdriver.Chrome()

        driver.get(url)

        time.sleep(3)

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(1)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        products = soup.find_all('link', {'itemprop': 'url'})

        for product in products:
            href = product.get('href')
            if href not in all_products_urls:
                all_products_urls.append(href)

        driver.quit()

print(f"Scraping done after {time.time() - all_products_start_time}")
print(f"Scraping product information and inserting into database...")

induvidual_products_start_time = time.time()

db = Connection()

price_pattern = r'Jmf-pris\s*(\d{1,3},\d{2})\s*kr/kg'

driver = webdriver.Chrome()

base_url = "https://www.willys.se"

for product_url in all_products_urls:

    driver.get(base_url + product_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    time.sleep(0.1)
    current_product = {}
    product_name = soup.find('span', {'itemprop': 'name'})
    price_tag = soup.find('div', class_='sc-a5c0d994-14 idsweN').find('p', class_='sc-3f3462ff-0 euMZRY')
    td_values = soup.find_all('td')

    current_product["name"] = product_name.text.strip()
    current_product["link"] = base_url + product_url.strip('\n')

    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 1 and 'kilokalori' in cols[1].text.lower():  # Check the first <td> for 'protein'
            kilokalori = [int(i) for i in cols[1].text.strip().split() if
                          i.isdigit()]  # Extract the second <td> (the protein value)
            current_product["energy"] = int(kilokalori[0])

        if len(cols) > 1 and 'protein' in cols[0].text.lower():  # Check the first <td> for 'protein'
            protein_value = [int(i) for i in cols[1].text.strip().split() if
                             i.isdigit()]  # Extract the second <td> (the protein value)
            current_product["protein"] = int(protein_value[0])

    price_match = re.search(price_pattern, price_tag.text.strip())
    if price_match:
        jmf_price_str = price_match.group(1)
        jmf_price_float = float(jmf_price_str.replace(',', '.'))
        current_product["price"] = jmf_price_float

    print(current_product)
    db.insert_product(current_product)

    time.sleep(5) # Willy's doesn't let me scrape faster than this

db.close()
driver.quit()

print(f"Scraping done after {time.time() - induvidual_products_start_time}")
