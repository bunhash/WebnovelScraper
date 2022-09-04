#!/usr/bin/python3
#
# Parses ranobes.net
#
# @author Brian Hession
# @email hessionb@gmail.com
#

import json
from bs4 import BeautifulSoup, NavigableString
import undetected_chromedriver as uc

class Parser:

    ##########################################################################
    # PUBLIC
    ##########################################################################

    def __init__(self, url):
        self._browser = uc.Chrome()
        self._browser.get(url)

        # Get Main HTML
        html = self._browser.page_source
        main_soup = BeautifulSoup(html, 'lxml')

        # Get ToC HTML
        toc = main_soup.find('a', {'title' : 'Go to table of contents'})
        if not toc or not toc.has_attr('href'):
            raise Exception('could not find table of contents')
        toc_url = 'https://ranobes.net{}'.format(toc['href'])
        self._browser.get(toc_url)
        html = self._browser.page_source
        toc_soup = BeautifulSoup(html, 'lxml')

        self._title = self._parse_title(toc_soup)
        self._author = self._parse_author(None)
        self._cover_url = self._parse_cover_url(main_soup)
        self._chapterlist = self._parse_chapter_list(toc_url)

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

    def _parse_title(self, toc_soup):
        data = None
        for script in toc_soup.find_all('script'):
            if 'window.__DATA__' in script.text:
                data = json.loads(script.text.strip().strip('window.__DATA__ = '))
                break
        if data == None:
            raise Exception('no chapter data found')
        return data['book_title'].encode('utf-8', errors='ignore')

    def _parse_author(self, soup):
        return 'ranobes.net'.encode('utf-8')

    def _parse_cover_url(self, soup):
        poster = soup.find('div', {'class' : 'poster'})
        if poster:
            url = poster.find('a')
            if url and url.has_attr('href'):
                return url['href']
        return None

    def _parse_chapter_list(self, toc_url):
        # Cycle through ToC
        chapterlist = list()
        page = 1
        page_url = toc_url
        while True:
            self._browser.get(page_url)
            toc_soup = BeautifulSoup(self._browser.page_source, 'lxml')
            data = None
            for script in toc_soup.find_all('script'):
                if 'window.__DATA__' in script.text:
                    data = json.loads(script.text.strip().strip('window.__DATA__ = '))
                    break
            if data == None:
                raise Exception('no chapter data found')
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
    with open('staging/995868.html', 'rb') as f:
        print(Parser.parse_chapter(f.read()))
