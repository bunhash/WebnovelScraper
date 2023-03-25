#!/usr/bin/python3
#
# Parses vipnovel.com
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import requests, time
from bs4 import BeautifulSoup, NavigableString
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Parser:

    ##########################################################################
    # PUBLIC
    ##########################################################################

    def __init__(self, url):
        self._url = url
        self._session = requests.Session()
        res = self._session.get(url)
        soup = BeautifulSoup(res.text, 'lxml')

        self._title = self._parse_title(soup)
        self._author = self._parse_author(soup)
        self._cover_url = self._parse_cover_url(soup)
        self._chapterlist = self._parse_chapter_list(soup)

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
        chapter = soup.find('div', { 'id' : 'js-truyenkk-read-content' })
        title_el = chapter.find('h4')

        # Parse title
        title = '???'
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter.find_all('p'):
            if len(p.text.strip()) > 0 and not p.has_attr('style'):
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

    def _parse_title(self, soup):
        title_el = soup.find('h1', { "class" : "title" })
        if not title_el:
            raise Exception('could not find title')
        return title_el.text.strip().encode('utf-8')

    def _parse_author(self, soup):
        return 'novelnb.net'.encode('utf-8')

    def _parse_cover_url(self, soup):
        div = soup.find('div', { "class" : "book" })
        return div.img['src']

    def _parse_chapter_list(self, soup):
        chapterlist = list()
        while True:
            div = soup.find('div', { "id" : "list-chapter" })
            if not div:
                break
            uls = div.find_all('ul', { "class" : "list-chapter" })
            if not uls:
                break
            for ul in uls:
                for a in ul.find_all('a'):
                    chapterlist.append(a['href'])
            next_page = div.find('a', { "rel" : "next" })
            if not next_page:
                break
            res = self._session.get(next_page['href'])
            soup = BeautifulSoup(res.text, 'lxml')
        return chapterlist
