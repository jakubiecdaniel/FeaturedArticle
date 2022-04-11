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

#https://stackoverflow.com/questions/45199076/take-full-page-screenshot-in-chrome-with-selenium   
def chrome_takeFullScreenshot(driver) :
  import json
  import base64
  def send(cmd, params):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd':cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    return response.get('value')

  def evaluate(script):
    response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
    return response['result']['value']

  metrics = evaluate( \
    "({" + \
      "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," + \
      "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," + \
      "deviceScaleFactor: window.devicePixelRatio || 1," + \
      "mobile: typeof window.orientation !== 'undefined'" + \
    "})")
  send('Emulation.setDeviceMetricsOverride', metrics)
  screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
  send('Emulation.clearDeviceMetricsOverride', {})

  return base64.b64decode(screenshot['data'])

def headless_pic(URL):

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=1')
    #options.add_argument('--window-size=1300,1000')

    #Todo, add check that chromedriver and chrome are installed
    try:
        driver = webdriver.Chrome(executable_path='C:\\chromedriver\\chromedriver.exe',chrome_options=options)
    except WebDriverException:
        print("Chromedriver needs to be installed.")
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
    
    scrollHeight = driver.execute_script("return document.body.scrollHeight")
    print(scrollHeight)
    inc = (scrollHeight / 10.0)
    scroll = 0
    for i in range(0,10):
        scrollTo = inc * (i + 1)
        ScrollScript = "window.scrollTo(0," + str(scrollTo) + ")"
        driver.execute_script(ScrollScript)
        time.sleep(2)
    driver.execute_script("window.scrollTo(0,0)")
    
    png = chrome_takeFullScreenshot(driver)

    with open("sc.png", 'wb') as f:
        f.write(png)
    
    driver.close()
    return 'sc.png'

def TakePicture(URL): 
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