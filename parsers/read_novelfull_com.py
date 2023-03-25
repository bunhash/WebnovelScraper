#!/usr/bin/python3
#
# Parses ranobes.net
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import string, time
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
        self._browser.close()

    def title(self):
        return self._title

    def author(self):
        return self._author

    def cover(self):
        return self._cover_url

    def chapters(self):
        return self._chapterlist

    @staticmethod
    def load(browser, url):
        browser.get(url)
        return browser.page_source.encode('utf-8', errors='ignore')

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')
        chapter_content = soup.find('div', {'id' : 'chr-content'})
        if not chapter_content:
            raise Exception('could not find chr-content')

        # Parse title
        title = '???'
        title_el = None
        for tab in ('h1', 'h2', 'h3', 'h4'):
            title_el = chapter_content.find(tab)
            if title_el:
                break
        if not title_el:
            title_el = soup.find('a', {'class' : 'chr-title'})
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter_content.find_all('p'):
            text = p.text.strip()
            if len(text) > 0:
                paragraphs.append(p)

        # Build chapter HTML
        chapter = BeautifulSoup('<html><head></head><body></body></html>', 'lxml')

        # Add title tag
        title_tag = chapter.new_tag('h1')
        title_tag.append(NavigableString(title))
        chapter.body.append(title_tag)

        # Add paragraphs
        for p in paragraphs:
            #para_tag = chapter.new_tag('p')
            #para_tag.append(NavigableString(p))
            #chapter.body.append(para_tag)
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
        title = Parser._wait_for(app, (By.XPATH, '//*[@id="novel"]/div[1]/div[1]/div[3]/h3'))
        title = title.text.strip()
        return string.capwords(title).encode('utf-8')

    def _parse_author(self, app):
        return 'read-novelfull.com'.encode('utf-8')

    def _parse_cover_url(self, app):
        image = Parser._wait_for(app, (By.XPATH, '//*[@id="novel"]/div[1]/div[1]/div[2]/div/div[2]/img'))
        return image.get_attribute('src')

    def _parse_chapter_list(self, app):
        # Cycle through ToC
        chapterlist = list()
        list_tab = Parser._wait_for(app, (By.XPATH, '//*[@id="tab-chapters-title"]'))
        list_tab.click()
        time.sleep(1)
        div = Parser._wait_for(app, (By.XPATH, '//*[@id="tab-chapters"]'))
        html = div.get_attribute('innerHTML').encode('utf-8')
        soup = BeautifulSoup(html, 'lxml')
        print(soup.prettify())
        for a in soup.find_all('a'):
            chapterlist.append(a['href'])
        if len(chapterlist) > 0:
            return chapterlist
        else:
            raise Exception('no chapters found')
