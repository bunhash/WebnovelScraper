#!/usr/bin/python3

import importlib, os, sys, urllib.parse

PARSERS = {
    'www.myboxnovel.com' : 'myboxnovel_com',
    'myboxnovel.com' : 'myboxnovel_com',
    'www.wuxiaworld.com' : 'wuxiaworld_com',
    'wuxiaworld.com' : 'wuxiaworld_com',
    'www.ranobes.net' : 'ranobes_net',
    'ranobes.net' : 'ranobes_net',
    'www.ranobes.top' : 'ranobes_net',
    'ranobes.top' : 'ranobes_net',
    'www.royalroad.com' : 'royalroad_com',
    'royalroad.com' : 'royalroad_com',
    'www.vipnovel.com' : 'vipnovel_com',
    'vipnovel.com' : 'vipnovel_com',
    'www.novelnb.net' : 'novelnb_net',
    'novelnb.net' : 'novelnb_net',
    'www.read-novelfull.com' : 'read_novelfull_com',
    'read-novelfull.com' : 'read_novelfull_com'
}

def build_parser(parser_name, url):
    parser_mod = importlib.import_module('parsers.{}'.format(parser_name), 'parsers')
    return parser_mod.Parser(url)

def load_bookinfo():
	with open('bookinfo.txt', 'r') as ifile:
		return ifile.readline().strip(), ifile.readline().strip(), ifile.readline().strip()

def main(args):
    # Variables
    title = str()
    author = str()
    url = str()
    chapters = list()
    write_bookinfo = False

    # Check arguments
    if len(args) == 0 and os.path.exists('bookinfo.txt'):
        title, author, url = load_bookinfo()
    elif len(args) == 1:
        url = args[0]
        write_bookinfo = True

    if len(url) == 0:
        print('Usage:', sys.argv[0], '<URL>')
        return 1

    # Load the parser
    url_info = urllib.parse.urlparse(url)
    domain = url_info.netloc
    if ':' in domain:
        domain = domain.split(':')[0]
    if domain not in PARSERS:
        print('ERROR :: no parser for', domain, file=sys.stderr)
        return 1
    parser = build_parser(PARSERS[domain], url)

    # Save title and author, if not saved.
    if write_bookinfo:
        title = parser.title()
        author = parser.author()

    print('Title:', title)
    print('Author:', author)
    print('Chapters:', len(parser.chapters()))

    if write_bookinfo:
        with open('bookinfo.txt', 'wb') as ofile:
            ofile.write(parser.title())
            ofile.write(b'\n')
            ofile.write(parser.author())
            ofile.write(b'\n')
            ofile.write(url.encode('utf-8'))
            ofile.write(b'\n')
    with open('urlcache.txt', 'w') as ofile:
        for url in parser.chapters():
            ofile.write('{}\n'.format(url))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
