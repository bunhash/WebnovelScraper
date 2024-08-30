#!/usr/bin/python3
#
# Parses ranobes.net
#
# @author bunhash
# @email bunhash@bhmail.me
#

import json, time
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
        pass

    def title(self):
        return self._title

    def author(self):
        return self._author

    def download_cover(self, filename):
        pass

    def chapters(self):
        return self._chapterlist

    @staticmethod
    def load(browser, url):
        browser.get(url)
        Parser._wait_for(browser, (By.XPATH, '//*[@id="arrticle"]'))
        return browser.page_source.encode('utf-8', errors='ignore')

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')

        # Parse title
        title = '???'
        title_el = soup.find('h1', {'class' : 'h4 title'})
        if title_el:
            for child in title_el.children:
                if isinstance(child, NavigableString):
                    t = child.text.strip()
                    if len(t) > 0:
                        title = t

        # Get the reading content
        paragraphs = list()
        story = soup.find('div', {'id' : 'arrticle'})
        if story:
            for p in story.find_all('p'):
                #paragraphs.append(p.text.strip())
                paragraphs.append(p)
            if len(paragraphs) == 0:
                for child in story.children:
                    if isinstance(child, NavigableString):
                        p = soup.new_tag('p')
                        p.append(child)
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
        return WebDriverWait(app, 30).until(EC.presence_of_element_located(tup))

    def _parse_title(self, app):
        title = Parser._wait_for(app, (By.XPATH, '/html/body/div[1]/div/div/div[2]/div/article/div[2]/div[1]/div/div[1]/h1/span[1]'))
        return title.text.encode('utf-8')

    def _parse_author(self, app):
        return 'ranobes.net'.encode('utf-8')

    def _parse_cover_url(self, app):
        image = Parser._wait_for(app, (By.XPATH, '/html/body/div[1]/div/div/div[2]/div/article/div[2]/div[1]/div/div[1]/div[2]/link'))
        return image.get_attribute('href')

    def _parse_chapter_list(self, app):
        # Cycle through ToC
        chapterlist = list()
        image = Parser._wait_for(app, (By.XPATH, '/html/body/div[1]/div/div/div[2]/div/article/div[2]/div[1]/div/div[1]/div[3]/div[2]/div/div[3]/a[2]'))
        toc_url = image.get_attribute('href')
        page_url = toc_url
        page = 1
        while True:
            self._browser.get(page_url)
            toc_soup = BeautifulSoup(self._browser.page_source, 'lxml')
            data = None
            for script in toc_soup.find_all('script'):
                if 'window.__DATA__' in script.text:
                    data = json.loads(script.text.strip().strip('window.__DATA__ = '))
                    break
            if data == None:
                time.sleep(1)
                continue
            for chapter in data['chapters']:
                chapterlist.append(chapter['link'])
            page = page + 1
            if page > int(data['pages_count']):
                break
            page_url = '{}/page/{}/'.format(toc_url, page)

        # Return chapter list in reverse order
        if len(chapterlist) > 0:
            return chapterlist[::-1]
        else:
            raise Exception('no chapters found')

if __name__ == '__main__':
    with open('staging/1974183.html', 'rb') as f:
        print(Parser.parse_chapter(f.read()))
