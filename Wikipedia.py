import bs4
import requests
import re
import os
import time

from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

def GetFeaturedArticleURL():
    baseURL = "https://en.wikipedia.org"
    FeaturedListURL = "https://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article"

    res = requests.get(FeaturedListURL)
    res.raise_for_status()

    soup = bs4.BeautifulSoup(res.text, features="html.parser")

    # TODO : make this better
    MainBG = soup.find_all('div', class_='MainPageBG')[1]

    li = MainBG.find_all('li')[0]

    href = li.find_all('a',href=True)[0]['href']

    FeaturedArticleURL = baseURL + href

    # Todo: Change to so this is not hardcoded
    FeaturedArticleURL = FeaturedArticleURL[:11] + 'm.' + FeaturedArticleURL[11:]

    print(FeaturedArticleURL)

    return FeaturedArticleURL




def TakePicture(URL): 
    browser = webdriver.Firefox()
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
        scroll = 0

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