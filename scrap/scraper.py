import urlparse
import requests
from lxml import html


class Scraper(object):

    def __init__(self, keyword, domain,
                 endpoint, query_string, page_string, search_css):
        self.keyword = keyword
        self.domain = domain
        self.endpoint = endpoint
        self.query_string = query_string
        self.page_string = page_string
        self.search_css = search_css

    def get_links(self):
        links = []
        for i in xrange(10):
            page = i * 10
            links += self._get_links(page=page)
        return links

    def _get_links(self, page):
        html_text = self._get_html(page)
        html_tree = html.fromstring(html_text)
        hyperlinks = html_tree.cssselect(self.search_css)
        links = [
            {
                'url': self.parse_href(hyperlink.get('href')),
                'rank': index + 1 + page
            }
            for index, hyperlink in enumerate(hyperlinks)
        ]
        links = [link for link in links if self.check_link(link['url'])]
        return links

    def _get_html(self, page):
        r = requests.get(self.endpoint,
                         params={self.query_string: self.keyword,
                                 self.page_string: page})
        return r.text

    def parse_href(self, link):
        pass

    def check_link(self, link):
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
        endpoint = 'https://www.google.com/search'
        query_string = 'q'
        page_string = 'start'
        search_css = 'li.g h3.r a'
        super(GoogleScraper, self).__init__(keyword, domain, endpoint,
                                            query_string, page_string,
                                            search_css)

    def parse_href(self, link):
        queries = urlparse.urlparse(link).query.split('&')
        for query in queries:
            if query.startswith('q='):
                url = query[2:]
                return url


class BaiduScraper(Scraper):

    def __init__(self, keyword, domain):
        endpoint = 'http://www.baidu.com/s'
        query_string = 'wd'
        page_string = 'pn'
        search_css = 'td.f h3.t a'
        super(BaiduScraper, self).__init__(keyword, domain, endpoint,
                                           query_string, page_string,
                                           search_css)

    def parse_href(self, link):
        r = requests.get(link, allow_redirects=False)
        url = r.headers.get('location')
        return url


class BingScraper(Scraper):

    def __init__(self, keyword, domain):
        endpoint = 'http://www.bing.com/search'
        query_string = 'q'
        page_string = 'first'
        search_css = 'li.sa_wr div.sb_tlst h3 a'
        super(BingScraper, self).__init__(keyword, domain, endpoint,
                                          query_string, page_string,
                                          search_css)

    def _get_html(self, page):
        r = requests.get(self.endpoint,
                         params={self.query_string: self.keyword,
                                 self.page_string: page + 1})
        return r.text

    def parse_href(self, link):
        return link
