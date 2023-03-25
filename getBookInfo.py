#!/usr/bin/python3

import importlib, subprocess, sys, urllib.parse

PARSERS = {
    'www.myboxnovel.com' : 'myboxnovel_com',
    'myboxnovel.com' : 'myboxnovel_com',
    'www.wuxiaworld.com' : 'wuxiaworld_com',
    'wuxiaworld.com' : 'wuxiaworld_com',
    'www.ranobes.net' : 'ranobes_net',
    'ranobes.net' : 'ranobes_net',
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

def main(args):
    if len(args) != 1:
        print('Usage:', sys.argv[0], '<URL>')
        return 1

    # Load the parser
    url_info = urllib.parse.urlparse(args[0])
    domain = url_info.netloc
    if ':' in domain:
        domain = domain.split(':')[0]

    # Check for a known parser
    if domain not in PARSERS:
        print('ERROR :: no parser for', domain, file=sys.stderr)
        return 1

    # Load the parser
    parser = build_parser(PARSERS[domain], args[0])

    print('Title:', parser.title())
    print('Author:', parser.author())
    print('Cover:', parser.cover())
    print('Chapters:', len(parser.chapters()))

    with open('bookinfo.txt', 'wb') as ofile:
        ofile.write(parser.title())
        ofile.write(b'\n')
        ofile.write(parser.author())
        ofile.write(b'\n')
    cover_url = parser.cover()
    if cover_url:
        subprocess.run(['powershell', '-Command', 'curl', '-OutFile', 'cover.jpg', cover_url])
    with open('urlcache.txt', 'w') as ofile:
        for url in parser.chapters():
            ofile.write('{}\n'.format(url))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
