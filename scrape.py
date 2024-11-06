from bs4 import BeautifulSoup
from selenium import webdriver
import time

start = time.time()

all_products = []

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
            if href not in all_products:
                all_products.append(href)

        driver.quit()


products_file = open("products.txt", "w")
for product in all_products:
    products_file.write(product + "\n")


print(f"Scraping performed in {time.time() - start} seconds!")
