import csv
import time
from seleniumwire import webdriver
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
import requests

def get_proxy():
    with open('proxy.txt') as f:
        proxies = f.readlines()
        for proxy in proxies:
            yield proxy.strip()

def check_wordpress(url):
    try:
        res = requests.get(url)
        response_text = res.text
        return 'wp-content' in response_text or 'wp-includes' in response_text
    except:
        return False

def parse_urls(driver, query):
    print('Loaded 100%')
    print('Parsing urls...')
    results = driver.find_elements(By.CSS_SELECTOR, 'a[data-ved]')
    unic_links = []
    for result in results:
        link_url = result.get_attribute('href')
        if link_url:
            if link_url.startswith('https'):
                domain = urlparse(link_url).netloc
                if domain not in unic_links:
                    unic_links.append(domain)
                    is_wordpress = check_wordpress(link_url)
                    if is_wordpress:
                        with open('output.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow((query, urlparse(link_url).netloc))
                            print(f'Writed {urlparse(link_url).netloc} to csv')

def google_search(driver, query):
    try:
        print('Searching for sites...')
        max_iters = 20
        for i in range(max_iters):
            driver.execute_script('window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"})')
            time.sleep(3)
            try:
                button = driver.find_element(By.CSS_SELECTOR, 'span[class="RVQdVd"]')
                if i != 20:
                    button.click()
                    time.sleep(3)
            except:
                continue
            loaded = round((i * max_iters) // 10)
            print(f'Loaded: {loaded}%', end='\r')
    except:
        parse_urls(driver, query)
    else:
        parse_urls(driver, query)
    finally:
        driver.quit()


def setup_browser(proxy, query):
    print('Wait for page loading...')
    driver = webdriver.Chrome(seleniumwire_options = {
        'proxy': {
            'http': proxy,
            'https': proxy,
            'no_proxy': 'localhost,127.0.0.1'
        }
    })
    driver.get(f'https://www.google.com/search?q={query}')
    time.sleep(10)
    return driver

def main():
    proxy_gen = get_proxy()
    with open('keywords.txt') as f:
        queries = f.readlines()
        proxy = next(proxy_gen)
        for query in queries:
            driver = setup_browser(proxy, query)
            try:
                driver.find_element(By.CSS_SELECTOR, 'div[class="capcha"]')
                print("CAPTCHA found, changing proxy...")
                driver.close()
                driver = setup_browser(next(proxy_gen), query)
                print('Proxy changed')
                google_search(driver, query.strip())
            except:
                print("CAPTCHA element not found")
                google_search(driver, query.strip())

if __name__ == "__main__":
    main()
