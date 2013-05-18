from gevent import monkey
monkey.patch_all()

import gevent
import requests
import urlparse
import urllib
from lxml import html
from scrap.cache import cache
from scrap.utils import chunks

MAX_PAGES = 20
CONCURRENCY = 20
CACHE_DURATION = 86400


class Scraper(object):

    def __init__(self, search_engine, keyword, domain,
                 endpoint, query_string, page_string, search_css):
        """
        The base class for all scrapers, the specific scrapers will
        set up the endpoint, query_string, page_string to form the
        search url of the search engine, and search_css represents the
        search result in the html
        """
        self.search_engine = search_engine
        self.keyword = keyword
        self.domain = domain
        self.endpoint = endpoint
        self.query_string = query_string
        self.page_string = page_string
        self.search_css = search_css

    @cache(CACHE_DURATION)
    def get_links(self, max_pages=MAX_PAGES):
        """
        Use gevent to download and parse search pages
        so that the http requests does not block the process
        """
        jobs = [gevent.spawn(self._get_links, i * 10)
                for i in xrange(max_pages)]
        # split jobs into trunks based on the concurrency
        job_chunks = chunks(jobs, CONCURRENCY)
        for jobs in job_chunks:
            gevent.joinall(jobs)

        links = []
        for jobs in job_chunks:
            for job in jobs:
                links += job.value
        return links

    def _get_links(self, page):
        try:
            html_text = self._get_html(page)
        except requests.ConnectionError:
            return [{'url': 'DNS error or connection refused', 'rank': 0}]
        except requests.Timeout:
            return [{'url': 'Request times out', 'rank': 0}]
        html_tree = html.fromstring(html_text)
        hyperlinks = html_tree.cssselect(self.search_css)
        # gevent is used here because for Baidu, it needs to get the actual
        # link by finding the http redirect
        jobs = [gevent.spawn(self._parse_hyperlink, hyperlink, index, page)
                for index, hyperlink in enumerate(hyperlinks)]
        # split jobs into trunks based on the concurrency
        job_chunks = chunks(jobs, CONCURRENCY)
        for jobs in job_chunks:
            gevent.joinall(jobs)

        links = []
        for jobs in job_chunks:
            links += [job.value for job in jobs]
        links = [link for link in links if self.check_link(link['url'])]
        return links

    def _parse_hyperlink(self, hyperlink, index, page):
        href = hyperlink.get('href')
        return {
            'url': self.parse_href(href),
            'rank': index + 1 + page
        }

    def _get_html(self, page):
        """download the result html from search engine"""
        r = requests.get(self.endpoint,
                         params={self.query_string: self.keyword,
                                 self.page_string: page})
        return r.text

    def parse_href(self, link):
        pass

    def check_link(self, link):
        """Check if the domain belongs to the link"""
        hostname = urlparse.urlparse(link).hostname
        if hostname and (
            hostname.split('.')[-(len(self.domain.split('.'))):] ==
            self.domain.split('.')
        ):
            return True
        else:
            return False


class GoogleScraper(Scraper):

    def __init__(self, keyword, domain):
        search_engine = 'Google'
        endpoint = 'https://www.google.com/search'
        query_string = 'q'
        page_string = 'start'
        search_css = 'li.g h3.r a'
        super(GoogleScraper, self).__init__(search_engine, keyword, domain,
                                            endpoint, query_string,
                                            page_string, search_css)

    def parse_href(self, href):
        """The destination url in the search results is after url="""
        queries = urlparse.urlparse(href).query.split('&')
        for query in queries:
            if query.startswith('url='):
                url = query[4:]
                return urllib.unquote(url)


class BaiduScraper(Scraper):

    def __init__(self, keyword, domain):
        search_engine = 'Baidu'
        endpoint = 'http://www.baidu.com/s'
        query_string = 'wd'
        page_string = 'pn'
        search_css = 'td.f h3.t a'
        super(BaiduScraper, self).__init__(search_engine, keyword, domain,
                                           endpoint, query_string,
                                           page_string, search_css)

    def parse_href(self, link):
        """
        The destination url is encoded,
        and we need to find the actual url from the redirect
        """
        r = requests.get(link, allow_redirects=False)
        url = r.headers.get('location')
        # sometimes Baidu return unencoded url
        if url is None:
            url = link
        return url


class BingScraper(Scraper):

    def __init__(self, keyword, domain):
        search_engine = 'Bing'
        endpoint = 'http://www.bing.com/search'
        query_string = 'q'
        page_string = 'first'
        search_css = 'li.sa_wr div.sb_tlst h3 a'
        super(BingScraper, self).__init__(search_engine, keyword, domain,
                                          endpoint, query_string,
                                          page_string, search_css)

    def _get_html(self, page):
        """Bing's page number is different here"""
        r = requests.get(self.endpoint,
                         params={self.query_string: self.keyword,
                                 self.page_string: page + 1})
        return r.text

    def parse_href(self, link):
        return link
