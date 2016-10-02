
import argparse
import fnmatch
import os
import re

import requests
from six.moves.urllib.parse import unquote


class Spider(object):
    def __init__(self, config):
        self._config = config
        self.jail = set()
        self.matching = set()
        self.to_visit = set()  # This could be a Queue if threading
        self.seen = set()
        self.out_dir = None
        self.out_file = None

    def run(self):
        while self.to_visit:
            page = self.to_visit.pop()
            try:
                self.visit(page)
            except Exception as err:
                print(err)

    def scrape(self, argv=None):
        parser = argparse.ArgumentParser(prog='alterego scrape')
        parser.add_argument('--jail', action='append')
        parser.add_argument('--matching', action='append')
        output = parser.add_mutually_exclusive_group()
        output.add_argument('--out-file', '-o')
        output.add_argument('--out-dir', '-d')
        parser.add_argument('start', nargs='+')
        args = parser.parse_args(argv)
        args.jail = args.jail or []
        args.jail += args.start
        self.jail = set(self.page_key(page) for page in args.jail)
        self.matching = set(self.page_key(page) for page in (args.matching or args.jail))
        self.out_dir = args.out_dir
        self.out_file = args.out_file
        self.to_visit = set(args.start)
        self.run()

    def matches(self, page_key):
        """Checks if a ``page_key`` is a content page
        """
        for host, path, params in self.matching:
            if page_key[0] == host:
                if page_key[1].startswith(path) or fnmatch.fnmatch(page_key[1], path):
                    return True
        return False

    def crawlable(self, page_key):
        """Checks if a ``page_key`` is in the restricted space
        """
        for host, path, params in self.jail:
            if page_key[0] == host:
                if page_key[1].startswith(path) or fnmatch.fnmatch(page_key[1], path):
                    return True
        return False

    @staticmethod
    def page_key(page):
        """Generates a hashable tuple of page parts that can match other forms
        """
        if '//' in page:
            proto_, page = page.split('//', 1)
        if '/' in page:
            host, page = page.split('/', 1)
        else:
            host = page
            page = ''
        host = host.lower()
        if host.startswith('www'):
            host = host.split('.', 1)[1]
        if '?' in page:
            path, params = page.split('?', 1)
        else:
            path = page
            params = ''
        if '#' in params:
            params = params.split('#', 1)[0]
        if '/' in path:
            base_path, tail = path.rsplit('/', 1)
            if 'index' in tail:
                path = base_path
        path = path.strip('/')
        return host, path, params

    def visit(self, page):
        page_key = self.page_key(page)
        if page_key in self.seen:
            return
        print('Visiting '+page)
        self.seen.add(page_key)
        crawlable = self.crawlable(page_key)
        if self.matches(page_key):
            self.save(page, crawlable)
        elif crawlable:
            self.fetch(page, True)

    def fetch(self, page, crawl=False):
        res = requests.get(page)
        res.raise_for_status()
        html = res.text
        html = re.sub(r'<script.*?</script>', '', html, flags=re.MULTILINE | re.DOTALL)
        html = re.sub(r'<style.*?</style>', '', html, flags=re.MULTILINE | re.DOTALL)
        match = re.search(r'<body.*</body>', html, flags=re.MULTILINE | re.DOTALL)
        if match is not None:
            html = match.group(0)
        if crawl:
            print('Crawling '+page)
            for match in re.finditer(r'href=(?P<quot>.)(?P<link>.*?)(?P=quot)', html):
                link = unquote(match.group('link'))
                redir = link.find('http', 4)
                link = link.replace('&amp;', '&')
                if redir != -1:
                    link = link[redir:]
                    link = link.replace('&amp;', '%amp;')
                    link = link.split('&', 1)[0]
                    link = link.replace('%amp;', '&amp;')
                self.to_visit.add(link)
        return html

    def save(self, page, crawl=False):
        """Requests and saves a remote page to a local file
        """
        print('Saving '+page)
        html = self.fetch(page, crawl)
        content = html.replace('</p>', '\n')
        content = re.sub(r'<.*?>', ' ', content)
        content = content.encode('utf8')
        if self.out_file:
            with open(self.out_file, 'a') as handle:
                handle.write(content+'\n')
        elif self.out_dir:
            page_key = self.page_key(page)
            try:
                os.makedirs(os.path.join(self.out_dir, page_key[0]))
            except OSError:
                pass
            filename = os.path.join(self.out_dir, page_key[0],
                                    (page_key[1]+'?'+page_key[2]).replace('/', '_'))
            with open(filename, 'w') as handle:
                handle.write(content)
