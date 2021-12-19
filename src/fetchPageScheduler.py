import os
import argparse
import requests
import urllib.request
from datetime import datetime
from typing import List, Type
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
# pip3 install selenium
from selenium import webdriver
# pip3 install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from threading import Thread

userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument(f'user-agent={userAgent}')

parser = argparse.ArgumentParser(description='Saves snapshot and page assets into a folder')
parser.add_argument('-u', '--urls', type=str, nargs='+', help='space separated urls to save')
parser.add_argument('-r', '--rootOutputFolder', type=str, help='root output folder path', default=os.getcwd())
args = parser.parse_args()

rootFolder = os.path.join(args.rootOutputFolder)
today = datetime.now().strftime('%Y-%m-%d')

allAssets = dict()

def fetchAllUrls(urls: List[str]):
    allThreads = list()
    for url in urls:
        crawlThread = Thread(target=crawl, args=(url, 0))
        crawlThread.start()
        snapshotThread = Thread(target=fetchSnapshot, args=(url,))
        snapshotThread.start()
        
        allThreads.extend((crawlThread, snapshotThread))
        
    for thread in allThreads:
        thread.join()
    dumpAssets(urls)

def crawl(rootUrl, depth=0):
    if depth < 0:
        return
    if rootUrl not in allAssets:
        content = urllib.request.urlopen(urllib.request.Request(rootUrl, \
            data=None, headers={'User-Agent': userAgent})).read()
        soup = BeautifulSoup(content)
        allAssets[rootUrl] = content.decode('utf-8')
        links = soup('a')
        for link in links:
            if 'href' in dict(link.attrs):
                url = urljoin(rootUrl, link['href'])
                if url.find("'") != -1:
                    continue
                url = url.split('#')[0] 
                if url[0:4] == 'http':
                    crawl(url, depth - 1)

def dumpAssets(urls: List[str]):
    for k, v in allAssets.items():
        outFolder = os.path.join(getOutputFolder(k), 'assets')
        outFolder = os.path.join(getOutputFolder(k), 'assets', 'nestedAssets')
        createFolderIfNotExist(outFolder)
        if k not in set(urls):
            with open(os.path.join(outFolder, 'nestedAssets', encodeUrl(k)), 'w') as f:
                f.write(v)
        else:
            with open(os.path.join(outFolder, getOutputFileName(k) + '.html'), 'w') as f:
                f.write(v)
                
def fetchSnapshot(url: str):
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
    driver.set_script_timeout(30)
    driver.get(url)
    
    expandWindow(driver)
    el = driver.find_element(By.XPATH, '//body')
    outFolder = os.path.join(getOutputFolder(url), 'scrsht')
    createFolderIfNotExist(outFolder)
    
    el.screenshot(os.path.join(outFolder, getOutputFileName(url) + '.png'))   
    driver.quit()
    
    
def expandWindow(driver: Type[webdriver.Chrome]):
    original_size = driver.get_window_size()
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    required_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(required_width, required_height)
        
def getOutputFolder(url: str) -> str:
    domain = urlparse(url).netloc
    return os.path.abspath(os.path.join(rootFolder, domain, today))

def getOutputFileName(url: str) -> str:
    urlParsed = urlparse(url)
    return (urlParsed.path + urlParsed.params + urlParsed.query + urlParsed.fragment).replace('/', ' ')

def createFolderIfNotExist(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)

def encodeUrl(url):
    return urllib.parse.quote(url)

if __name__ == "__main__":
    createFolderIfNotExist(rootFolder)
    fetchAllUrls(list(args.urls))
    