import bs4
import requests
import re
import os
import time

from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException 
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def GetFeaturedArticleURL():
    baseURL = "https://en.wikipedia.org"
    FeaturedListURL = "https://en.wikipedia.org/wiki/Main_Page"

    res = requests.get(FeaturedListURL)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features="html.parser")
    try:
        MainBG = soup.find_all('div', id='mp-tfa')[0]

        bold = MainBG.find('b')

        href = bold.find_all('a',href=True)[0]['href']
    except IndexError:
        print('Failed to find featured article')
        return False

    FeaturedArticleURL = baseURL + href

    # Todo: Change to so this is not hardcoded
    FeaturedArticleURL = FeaturedArticleURL[:11] + 'm.' + FeaturedArticleURL[11:]

    print(FeaturedArticleURL)

    return FeaturedArticleURL

def chrome_headless_picture(URL):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=1')
    options.add_argument('--no-sandbox')

    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    except WebDriverException as err:
        print(err)
        return False
    
    print(driver.get_window_size())
    driver.get(URL)
    
    try:
        notes_el = driver.find_element_by_id("Notes")
        notes_el.click()
    except NoSuchElementException:
        pass
    try:
        ref_el = driver.find_element_by_id("References")
        ref_el.click()
    except NoSuchElementException:
        pass
    try:
        extlinks_el = driver.find_element_by_id("External_links")
        extlinks_el.click()
    except NoSuchElementException:
        pass
    try:
        sources_el = driver.find_element_by_id("Sources")
        sources_el.click()
    except NoSuchElementException:
        pass
    
    scrollHeight = driver.execute_script("return document.body.scrollHeight")
    
    inc = (scrollHeight / 10.0)
    
    for i in range(0,10):
        scrollTo = inc * (i + 1)
        ScrollScript = "window.scrollTo(0," + str(scrollTo) + ")"
        driver.execute_script(ScrollScript)
        time.sleep(2)
    driver.execute_script("window.scrollTo(0,0)")
    
    #https://stackoverflow.com/questions/41721734/take-screenshot-of-full-page-with-selenium-python-with-chromedriver/57338909#57338909

    width = driver.execute_script('return document.body.parentNode.scrollWidth')
    height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(width,height)
    
    driver.find_element_by_xpath('//*[@id="content"]').screenshot('sc.png')
    
    driver.close()
    return 'sc.png'

def firefox_picture(URL): 
    try:
        browser = webdriver.Firefox()
    except WebDriverException:
        print("Geckodriver needs to be installed.")
        return False
    try:
        browser.get(URL)
        browser.set_context("chrome")
        html = browser.find_element_by_tag_name("html")

        html.send_keys(Keys.CONTROL + "+")
        html.send_keys(Keys.CONTROL + "+")
        html.send_keys(Keys.CONTROL + "+")
        html.send_keys(Keys.CONTROL + "+")

        browser.set_context("content")
        
        try:
            notes_el = browser.find_element_by_id("Notes")
            notes_el.click()
        except NoSuchElementException:
            pass

        try:
            ref_el = browser.find_element_by_id("References")
            ref_el.click()
        except NoSuchElementException:
            pass

        try:
            extlinks_el = browser.find_element_by_id("External_links")
            extlinks_el.click()
        except NoSuchElementException:
            pass
 
        scrollHeight = browser.execute_script("return document.body.scrollHeight")

        inc = (scrollHeight / 10.0)
        

        for i in range(0,10):
            scrollTo = inc * (i + 1)
            ScrollScript = "window.scrollTo(0," + str(scrollTo) + ")"
            browser.execute_script(ScrollScript)
            time.sleep(2)


        browser.execute_script("window.scrollTo(0,0)")

        el = browser.find_element_by_xpath('//*[@id="content"]')

        el.screenshot("sc.png")
    finally:
        browser.close()

    return 'sc.png'
