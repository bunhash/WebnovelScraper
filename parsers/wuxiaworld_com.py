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

        # Get app
        app = self._browser.find_element(By.ID, 'app')

        self._title = self._parse_title(app)
        self._author = self._parse_author(None)
        self._cover_url = self._parse_cover_url(app)
        self._chapterlist = self._parse_chapter_list(app)

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
        browser.get('https://wuxiaworld.com')
        account_btn = browser.find_element(By.XPATH, '//*[@id="header"]/div/div/div[3]/button')
        account_btn.click()
        # Dumb Chrome workaround
        popup = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]')))
        for button in browser.find_elements(By.TAG_NAME, 'button'):
            if 'LOG IN' in button.text:
                button.click()
        login_form = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div[2]/form')))
        time.sleep(1)
        username_field = login_form.find_element(By.ID, 'Username')
        username_field.send_keys(username)
        time.sleep(1)
        password_field = login_form.find_element(By.ID, 'Password')
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

    @staticmethod
    def load(browser, url):
        browser.get(url)
        app = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'app')))
        chapters = None
        for i in range(10):
            html = app.get_attribute('innerHTML').encode('utf-8')
            soup = BeautifulSoup(html, 'lxml')
            chapters = [div for div in soup.findAll('div') if div.has_attr('class') and 'chapter-content' in div['class']]
            if not chapters:
                continue
            return html
        raise Exception('could not find chapter')

    @staticmethod
    def parse_chapter(html):
        soup = BeautifulSoup(html, 'lxml')
        chapters = [div for div in soup.findAll('div') if div.has_attr('class') and 'chapter-content' in div['class']]
        if not chapters:
            raise Exception('could not find chapter')
        chapter = chapters[0]
        parent = chapter.parent

        # Parse title
        title = '???'
        title_el = parent.find('h4')
        if title_el:
            title = title_el.text.strip()

        # Get the reading content
        paragraphs = list()
        for p in chapter.find_all('p'):
            paragraphs.append(p.text.strip())

        # Build chapter HTML
        chapter = BeautifulSoup('<html><head></head><body></body></html>', 'lxml')

        # Add title tag
        title_tag = chapter.new_tag('h1')
        title_tag.append(NavigableString(title))
        chapter.body.append(title_tag)

        # Add paragraphs
        for p in paragraphs:
            para_tag = chapter.new_tag('p')
            para_tag.append(NavigableString(p))
            chapter.body.append(para_tag)
        
        # Return chapter title and chapter html
        return title.encode('utf-8', errors='ignore'), chapter.encode('utf-8', errors='ignore')
    
    ##########################################################################
    # PRIVATE
    ##########################################################################

    def _parse_title(self, app):
        header = app.find_element(By.TAG_NAME, 'h1')
        return header.text.encode('utf-8')

    def _parse_author(self, app):
        return 'wuxiaworld.com'.encode('utf-8')

    def _parse_cover_url(self, app):
        image = app.find_element(By.TAG_NAME, 'img')
        full_url = image.get_attribute('src')
        return full_url[full_url.index('https://cdn.wuxiaworld.com'):]

    def _parse_chapter_list(self, app):
        chapterlist = list()
        chapter_tab = app.find_element(By.ID, 'full-width-tab-1')
        chapter_tab.click()
        chapter_list = WebDriverWait(app, 10).until(EC.presence_of_element_located((By.ID, 'full-width-tabpanel-1')))
        sections = chapter_list.find_elements(By.XPATH, '//*[@id="full-width-tabpanel-1"]/div/div/div[2]/div')
        sections[0].find_element(By.TAG_NAME, 'div').click()
        for s in sections:
            tab = s.find_element(By.TAG_NAME, 'div')
            tab.click()
            time.sleep(1)
            for chapter in s.find_elements(By.TAG_NAME, 'a'):
                chapterlist.append(chapter.get_attribute('href'))
            tab.click()
            time.sleep(1)
        return chapterlist[::-1]

if __name__ == '__main__':
    with open('staging/emperor-chapter-4308', 'rb') as f:
        print(Parser.parse_chapter(f.read()))
