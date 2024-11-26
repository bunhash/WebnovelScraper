#!/usr/bin/python
#
# Parses myboxnovel.com
#
# @author bunhash
# @email bunhash@bhmail.me
#

import re, requests, socket
from bs4 import BeautifulSoup, NavigableString
from urllib.error import URLError

class Parser:

    ###########################################################################
    # PUBLIC
    ###########################################################################

    def __init__(self, url, useragent='EpubFetcher (+fetcher.py)'):
        self._session = requests.Session()
        self._url = url.rstrip('/')
        soup = BeautifulSoup(self._session.get(url).content, 'lxml')
        self._title = self._parse_title(soup)
        self._author = self._parse_author(soup)
        self._cover_url = self._parse_cover_url(soup)
        self._chapterlist = self._parse_chapter_list(soup)

    def title(self):
        return self._title

    def author(self):
        return self._author

    def download_cover(self, filename):
        raise Exception("Failed")

    def chapters(self):
        return self._chapterlist

    @staticmethod
    def parse_chapter(html):
        webpage = BeautifulSoup(html, 'lxml')

        # Get the chapter title
        title = '???'
        title_contents = webpage.find('div', {'id' : 'manga-reading-nav-head'})
        if title_contents:
            active = title_contents.find('li', {'class' : 'active'})
            if active:
                title = active.text.strip()

        # Get the reading content
        paragraphs = list()
        reading_contents = webpage.find('div', {'class' : 'reading-content'})
        for p in reading_contents.find_all('p'):
            paragraphs.append(str(p.text).strip())

        # Build chapter HTML
        chapter = BeautifulSoup('<html><head></head><body></body></html>', 'lxml')

        # Add title tag
        title_tag = chapter.new_tag('h1')
        title_tag.append(NavigableString(title))
        chapter.body.append(title_tag)

        # Add paragraphs
        for p in paragraphs:
            contents = ' '.join([l.strip() for l in p.split('\n')])
            contents = contents.replace('\u00a0', '')
            para_tag = chapter.new_tag('p')
            para_tag.append(NavigableString(contents))
            chapter.body.append(para_tag)
        
        # Return chapter title and chapter html
        return title.encode('utf-8', errors='ignore'), chapter.encode('utf-8', errors='ignore'), []

    ###########################################################################
    # PRIVATE
    ###########################################################################

    def _parse_title(self, soup):
        meta = soup.find('meta', {'property' : 'og:title'})
        if meta and meta.has_attr('content'):
            return meta['content'].encode('utf-8')
        return None

    def _parse_author(self, soup):
        return 'myboxnovel.com'.encode('utf-8')

    def _parse_cover_url(self, soup):
        meta = soup.find('meta', {'property' : 'og:image'})
        if meta and meta.has_attr('content'):
            return meta['content']
        return None

    def _parse_chapter_list(self, soup):
        res = None
        if 'myboxnovel' in self._url:
            chapter_id = soup.find('div', {'id' : 'manga-chapters-holder'})
            if chapter_id and chapter_id.has_attr('data-id'):
                res = self._session.post('https://myboxnovel.com/wp-admin/admin-ajax.php', data={
                    'action' : 'manga_get_chapters',
                    'manga' : chapter_id['data-id']
                })
            else:
                raise Exception('[myboxnovel.com] :: could not find book id')
        else:
            res = self._session.post(self._url + '/ajax/chapters')
        soup = BeautifulSoup(res.content, 'lxml')
        chapterlist = list()
        for li in soup.find_all('li', {'class' : 'wp-manga-chapter'}):
            a = li.find('a')
            if a and a.has_attr('href'):
                chapterlist.append(a['href'].strip('/'))
        return chapterlist[::-1]
