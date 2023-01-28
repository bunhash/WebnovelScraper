#!/usr/bin/python3

import getopt, importlib, os, multiprocessing, requests, subprocess, sys, time, urllib.parse
import undetected_chromedriver as uc

PARSERS = {
    'www.myboxnovel.com' : 'myboxnovel_com',
    'myboxnovel.com' : 'myboxnovel_com',
    'www.wuxiaworld.com' : 'wuxiaworld_com',
    'wuxiaworld.com' : 'wuxiaworld_com',
    'www.ranobes.net' : 'ranobes_net',
    'ranobes.net' : 'ranobes_net',
    'www.royalroad.com' : 'royalroad_com',
    'royalroad.com' : 'royalroad_com'
}
LOADED = {}

def load_parser(url):
    # Load the parser
    url_info = urllib.parse.urlparse(url)
    domain = url_info.netloc
    if ':' in domain:
        domain = domain.split(':')[0]
    if domain not in LOADED:
        LOADED[domain] = importlib.import_module('parsers.{}'.format(PARSERS.get(domain)), 'parsers')
    return LOADED[domain]

class Selenium:

    def __init__(self, urls, username=None, password=None):
        self._parser = load_parser(urls[0])
        self._urls = urls
        self._browser = uc.Chrome()
        if username and password:
            self._parser.Parser.login(self._browser, username, password)

    def __del__(self):
        self._browser.quit()

    def download(self, url):
        filename = url.rsplit("/", 1)[1]
        if not filename:
            raise Exception('no filename found')
        staging_file = os.path.join('staging', filename)
        if not os.path.exists(staging_file):
            with open(staging_file, 'wb') as ofile:
                ofile.write(self._parser.Parser.load(self._browser, url))

class PowerShell:

    def __init__(self, urls):
        self._pool = multiprocessing.Pool(processes=20)
        self._jobs = dict()
        for url in urls:
            self._jobs[url] = self._pool.apply_async(PowerShell._download, (url,))
        self._pool.close()

    def __del__(self):
        self._pool.terminate()
        self._pool.join()

    @staticmethod
    def _download(url):
        filename = url.rsplit("/", 1)[1]
        if not filename:
            raise Exception('no filename found')
        staging_file = os.path.join('staging', filename)
        if not os.path.exists(staging_file):
            return subprocess.run(['powershell', '-Command', 'Invoke-WebRequest', '-OutFile', staging_file, url], capture_output=True)
        return 0

    def download(self, url):
        if url in self._jobs.keys():
            ret_code = self._jobs[url].get(timeout=None)
            if ret_code != 0:
                print('ERROR :: download for failed ({})'.format(url), file=sys.stderr)
        else:
            print('ERROR :: {} not in jobs'.format(url), file=sys.stderr)

class Native:

    def __init__(self, urls):
        self._pool = multiprocessing.Pool(processes=20)
        self._jobs = dict()
        for url in urls:
            self._jobs[url] = self._pool.apply_async(Native._download, (url,))
        self._pool.close()

    def __del__(self):
        self._pool.terminate()
        self._pool.join()

    @staticmethod
    def _download(url):
        filename = url.rsplit("/", 1)[1]
        if not filename:
            raise Exception('no filename found')
        staging_file = os.path.join('staging', filename)
        if not os.path.exists(staging_file):
            res = requests.get(url)
            if res.status_code != 200:
                return int(res.status_code)
            with open(staging_file, 'wb') as ofile:
                ofile.write(res.content)
        return 0

    def download(self, url):
        if url in self._jobs.keys():
            ret_code = self._jobs[url].get(timeout=None)
            if ret_code != 0:
                print('ERROR :: download for failed ({})'.format(url), file=sys.stderr)
        else:
            print('ERROR :: {} not in jobs'.format(url), file=sys.stderr)

def main(args):
    use_selenium = False
    use_powershell = False
    username = None
    password = None
    opts, args = getopt.getopt(args, "hSPu:p:")
    for o, a in opts:
        if o == "-h":
            print('Usage: {} [-S]'.format(sys.argv[0]))
            print('')
            print('  -h            print this message')
            print('  -S            use Selenium')
            print('  -P            use PowerShell')
            print('  -u username   username')
            print('  -p password   password')
            return 0
        elif o == "-S":
            use_selenium = True
            use_powershell = False
        elif o == "-P":
            use_selenium = False
            use_powershell = True
        elif o == "-u":
            username = a
        elif o == "-p":
            password = a
        else:
            assert False, "unhandled option"

    urls = list()
    for line in sys.stdin:
        urls.append(line.strip())

    downloader = None
    if use_selenium:
        downloader = Selenium(urls, username, password)
    elif use_powershell:
        downloader = PowerShell(urls)
    else:
        downloader = Native(urls)

    if not os.path.exists('staging'):
        os.mkdir('staging')

    total = len(urls)
    for i in range(total):
        print('({:4d}/{:4d}) Downloading'.format(i + 1, total), urls[i])
        downloader.download(urls[i])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
