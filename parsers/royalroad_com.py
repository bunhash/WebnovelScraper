#!/usr/bin/python3
#
# Parses wuxiaworld.com
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import time
from bs4 import BeautifulSoup, NavigableString
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Parser:

    ##########################################################################
    # PUBLIC
    ##########################################################################

    def __init__(self, url):
        self._browser = uc.Chrome()
        self._browser.get(url)

        self._title = self._parse_title(self._browser)
        time.sleep(1)
        self._author = self._parse_author(self._browser)
        time.sleep(1)
        self._cover_url = self._parse_cover_url(self._browser)
        time.sleep(1)
        self._chapterlist = self._parse_chapter_list(self._browser)

    def __del__(self):
        self._browser.quit()
        #self._browser.close()

    def title(self):
        return self._title

    def author(self):
        return self._author

    def cover(self):
        return self._cover_url

    def chapters(self):
        return self._chapterlist

    @staticmethod
    def login(browser, username, password):
        raise Exception("not implemented")

    @staticmethod
    def load(browser, url):
        browser.get(url)
        content = Parser._wait_for(browser, (By.CLASS_NAME, 'chapter-page'))
        return content.get_attribute('innerHTML').encode('utf-8')

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')
        chapter = soup.find('div', {'class' : 'chapter-content'})
        if not chapter:
            raise Exception('could not find chapter')

        # Parse title
        title = '???'
        title_el = soup.find('h1')
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter.find_all('p'):
            paragraphs.append(p)

        # Build chapter HTML
        chapter = BeautifulSoup('<html><head></head><body></body></html>', 'lxml')

        # Add title tag
        title_tag = chapter.new_tag('h1')
        title_tag.append(NavigableString(title))
        chapter.body.append(title_tag)

        # Add paragraphs
        for p in paragraphs:
            chapter.body.append(p)
        
        # Return chapter title and chapter html
        return title.encode('utf-8', errors='ignore'), chapter.encode('utf-8', errors='ignore')
    
    ##########################################################################
    # PRIVATE
    ##########################################################################

    @staticmethod
    def _wait_for(app, tup):
        return WebDriverWait(app, 10).until(EC.presence_of_element_located(tup))

    def _parse_title(self, app):
        header = Parser._wait_for(app, (By.XPATH, '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/h1'))
        return header.text.encode('utf-8')

    def _parse_author(self, app):
        return 'royalroad.com'.encode('utf-8')

    def _parse_cover_url(self, app):
        image = Parser._wait_for(app, (By.XPATH, '/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[1]/div/img'))
        return image.get_attribute('src')

    def _parse_chapter_list(self, app):
        chapterlist = list()
        while True:
            chapter_tab = Parser._wait_for(app, (By.ID, 'chapters'))
            tbody = chapter_tab.find_element(By.TAG_NAME, 'tbody')
            for row in tbody.find_elements(By.TAG_NAME, 'tr'):
                link = row.find_element(By.TAG_NAME, 'a')
                chapterlist.append(link.get_attribute('href'))
            navigation_bar = Parser._wait_for(app, (By.XPATH, '/html/body/div[3]/div/div/div/div[1]/div/div[2]/div/div[2]/div[5]/div[2]/div/div/div[2]/div/ul'))
            arrows = navigation_bar.find_elements(By.CLASS_NAME, 'nav-arrow')
            if len(arrows) == 2:
                arrows[1].click()
            else:
                try:
                    right_arrow = arrows[0].find_element(By.CLASS_NAME, 'fa-chevron-right')
                    right_arrow.click()
                except:
                    break
        return chapterlist
