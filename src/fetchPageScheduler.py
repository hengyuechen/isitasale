import os
import argparse
import requests
import urllib.request
from datetime import datetime
from typing import List, Type
from urllib.parse import urlparse
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
        snapshotThread = Thread(target=fetchSnapshot, args=(url,))
        snapshotThread.start()
        
        allThreads.extend((crawlThread, snapshotThread))
        
    for thread in allThreads:
        thread.join()

def dumpAsset(url: str, driver):
        outFolder = os.path.join(getOutputFolder(url), 'assets')
        createFolderIfNotExist(outFolder)
        with open(os.path.join(outFolder, getOutputFileName(url) + '.html'), 'w') as f:
            f.write(driver.page_source)
                
def fetchSnapshot(url: str):
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chromeOptions)
    driver.set_script_timeout(30)
    driver.get(url)
    
    expandWindow(driver)
    el = driver.find_element(By.XPATH, '//body')
    outFolder = os.path.join(getOutputFolder(url), 'scrsht')
    createFolderIfNotExist(outFolder)
    
    el.screenshot(os.path.join(outFolder, getOutputFileName(url) + '.png')) 
    dumpAsset(url, driver)  
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
    