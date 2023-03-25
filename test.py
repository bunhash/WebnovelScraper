#!/usr/bin/python3

import requests, sys

def main(args):
    session = requests.Session()
    res = session.post("https://vipnovel.com/vipnovel/godly-stay-home-dad/ajax/chapters", data={})
    print(res.text)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
