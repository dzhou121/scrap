from gevent import monkey
monkey.patch_all()

import gevent
import requests
import urlparse
import urllib
import redis
import simplejson as json
from lxml import html
from scrap import settings
from scrap.utils import chunks


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
        self.redis_conn = redis.Redis(host=settings.REDIS_HOST,
                                      port=settings.REDIS_PORT,
                                      db=settings.REDIS_DB,
                                      password=settings.REDIS_PW)
        params_dict = {
            'search_engine': search_engine,
            'keyword': keyword,
            'domain': domain
        }
        self.scrap_task_status = settings.SCRAP_TASK_STATUS % params_dict
        self.scrap_task_result = settings.SCRAP_TASK_RESULT % params_dict

    def get_links_task(self, max_pages=settings.MAX_PAGES):
        """
        Use gevent to download and parse search pages
        so that the http requests does not block the process
        """
        if self.redis_conn.get(self.scrap_task_status) is not None:
            return

        self.redis_conn.set(self.scrap_task_status, 'pending')

        jobs = [gevent.spawn(self._get_links, i * 10)
                for i in xrange(max_pages)]
        # split jobs into trunks based on the concurrency
        job_chunks = chunks(jobs, settings.CONCURRENCY)
        for jobs in job_chunks:
            gevent.joinall(jobs)

        self.redis_conn.set(self.scrap_task_status, 'ok')
        self.redis_conn.expire(self.scrap_task_status, settings.CACHE_DURATION)
        self.redis_conn.expire(self.scrap_task_result, settings.CACHE_DURATION)

    def _get_links(self, page):
        try:
            html_text = self._get_html(page)
        except requests.ConnectionError:
            return self._store_link(
                {'rank': 0, 'url': 'DNS error or connection refused'})
        except requests.Timeout:
            return self._store_link(
                {'rank': 0, 'url': 'Request times out'})
        html_tree = html.fromstring(html_text)
        hyperlinks = html_tree.cssselect(self.search_css)
        # gevent is used here because for Baidu, it needs to get the actual
        # link by finding the http redirect
        jobs = [gevent.spawn(self._parse_hyperlink, hyperlink, index, page)
                for index, hyperlink in enumerate(hyperlinks)]
        # split jobs into trunks based on the concurrency
        job_chunks = chunks(jobs, settings.CONCURRENCY)
        for jobs in job_chunks:
            gevent.joinall(jobs)

    def _parse_hyperlink(self, hyperlink, index, page):
        """ get the href from the lxml html tree object, parse the href,
        and then check if the link belongs to the domain
        and store the one that do
        """
        href = hyperlink.get('href')
        url = self.parse_href(href)
        if not self.check_link(url):
            return None

        rank = index + 1 + page
        link = {
            'rank': rank,
            'url': url,
        }
        return self._store_link(link)

    def _store_link(self, link):
        """ Store the link result in Redis """
        link = json.dumps(link)
        self.redis_conn.sadd(self.scrap_task_result, link)
        return link

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
        search_engine = 'google'
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
        search_engine = 'baidu'
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
        search_engine = 'bing'
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
