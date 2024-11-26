#!/usr/bin/python3

import importlib, sys, os, multiprocessing, urllib.parse

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

def main(args):
    if not os.path.exists('book'):
        os.mkdir('book')

    pool = multiprocessing.Pool(processes=20)
    jobs = list()
    try:
        # Create the parsing jobs
        count = 0
        for line in sys.stdin:
            url = line.strip()
            if not url:
                continue
            count = count + 1
            raw_filename = os.path.join('staging', url.rstrip('/').split('/')[-1])
            if not raw_filename:
                print('Bad raw_filename:', url, file=sys.stderr)
                continue
            if not os.path.exists(raw_filename):
                print('File does not exist:', raw_filename, file=sys.stderr)
                continue
            parsed_filename = os.path.join('book', '{:04d}.html'.format(count))
            _ = load_parser(url) # Load the parser first so no race condition occurs
            jobs.append((raw_filename, pool.apply_async(parse, (url, raw_filename, parsed_filename))))
        pool.close()

        # Complete the parsing jobs
        images = list()
        with open('chapterlist.txt', 'w') as ofile:
            total = len(jobs)
            for i in range(total):
                raw, res = jobs[i]
                print('({:4d}/{:4d}) Parsing'.format(i + 1, total), raw)
                try:
                    ofname, ctitle, imgtups = res.get(timeout=None)
                    ofile.write('{} {}\n'.format(ofname, ctitle))
                    for imgtup in imgtups:
                        images.append(imgtup)
                except KeyboardInterrupt as e:
                    raise e
                except Exception as e:
                    print(e)

        # Write image URLs if any
        if len(images) > 0:
            with open('images.txt', 'w') as ofile:
                for imgurl, imgname in images:
                    ofile.write('{} {}\n'.format(imgurl, imgname))

    except KeyboardInterrupt:
        pool.terminate()
        pool.join()

def parse(url, ifname, ofname, prefix=None):
    if prefix == None:
        prefix = os.path.basename(ofname)
    try:
        parser = load_parser(url)
        with open(ifname, 'rb') as ifile:
            ctitle, chapter, images = parser.Parser.parse_chapter(ifile.read())
            ctitle = ctitle.decode('ascii', errors='ignore')
            imgtups = list()
            for i in range(len(images)):
                if images[i] != None:
                    index = images[i].rfind('.')
                    if index >= 0:
                        ext = images[i][index:]
                        imgname = '{}-{}{}'.format(prefix, str(i), ext)
                        imgtups.append((images[i], imgname))
                        chapter = chapter.replace(images[i].encode('utf-8'), imgname.encode('utf-8'))
            with open(ofname, 'wb') as ofile:
                ofile.write(chapter)
            return ofname, ctitle, imgtups
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        raise Exception('Error parsing {}->{}: {}'.format(ifname, ofname, e))

if __name__ == '__main__':
    main(sys.argv[1:])
