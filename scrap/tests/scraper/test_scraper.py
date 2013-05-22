import redis
import requests
import simplejson as json

from scrap.scraper.scraper import GoogleScraper, BaiduScraper, BingScraper
from scrap import test


class FakeRedis(object):
    """ Fake Redis class so that we don't actually call Redis """

    def __init__(self, *args, **kwargs):
        self.data = {}

    def get(self, key):
        return self.data.get(key, None)

    def sadd(self, key, value):
        if key not in self.data:
            self.data[key] = set()

        self.data[key].add(value)
        return True

    def smembers(self, key):
        return self.data.get(key, set())

    def set(self, key, value):
        self.data[key] = value
        return True

    def expire(self, key, duration):
        return True


class GoogleScraperTest(test.TestCase):

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(GoogleScraperTest, self).setUp()
        self.stubs.Set(redis, 'Redis', FakeRedis)
        self.google_scraper = GoogleScraper('test', 'test.com')

    def test_get_links_task_task(self):
        def fake_get_html(page):
            return """
            <html>
            <body>
                <li class="g">
                    <h3 class="r">
                        <a href="/url?q=http%3A%2F%2Ftest.com%2F">link 1</a>
                    </h3>
                </li>
                <li class="g">
                    <h3 class="r">
                        <a href="/url?q=http%3A%2F%2Ftesttest.com%2F">
                            link 2
                        </a>
                    </h3>
                </li>
                <li class="g">
                    <h3 class="r">
                        <a href="/url?q=http%3A%2F%2Fwww.test.com%2F">
                            link 3
                        </a>
                    </h3>
                </li>
            </body>
            </html>
            """
        self.stubs.Set(self.google_scraper, '_get_html', fake_get_html)
        self.google_scraper.get_links_task(max_pages=1)
        expected_links = [{'rank': 1, 'url': 'http://test.com/'},
                          {'rank': 3, 'url': 'http://www.test.com/'}]
        links = self.google_scraper.redis_conn.smembers(
            self.google_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_get_links_task_connection_error(self):
        """
        We want the result show DNS error or connection refused
        when it has problems when getting HTTP response
        """
        self.stubs.Set(self.google_scraper,
                       'endpoint', 'http://google_blocked/')
        self.google_scraper.get_links_task(max_pages=1)
        expected_links = [{'rank': 0,
                           'url': 'DNS error or connection refused'}]
        links = self.google_scraper.redis_conn.smembers(
            self.google_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_parse_href_encoded(self):
        href = '/url?q=http%3A%2F%2Ftest.com%2F'
        expected_url = 'http://test.com/'
        self.assertEqual(expected_url,
                         self.google_scraper.parse_href(href))

    def test_parse_href_unencoded(self):
        href = '/url?q=http://test.com/'
        expected_url = 'http://test.com/'
        self.assertEqual(expected_url,
                         self.google_scraper.parse_href(href))

    def test_check_link(self):
        link = 'http://www.test.com/test'
        self.assertEqual(True,
                         self.google_scraper.check_link(link))

        link = 'http://www.testtest.com/test'
        self.assertEqual(False,
                         self.google_scraper.check_link(link))


class BaiduScraperTest(test.TestCase):

    def setUp(self):
        super(BaiduScraperTest, self).setUp()
        self.stubs.Set(redis, 'Redis', FakeRedis)
        self.baidu_scraper = BaiduScraper('test', 'test.com')

    def test_get_links_task(self):
        def fake_get_html(page):
            return """
            <html>
            <body>
                <table>
                <tr><td class="f">
                    <h3 class="t">
                        <a href="http://www.baidu.com/link?url=fake1">link1</a>
                    </h3>
                </td></tr>
                <tr><td class="f">
                    <h3 class="t">
                        <a href="http://www.baidu.com/link?url=fake2">link2</a>
                    </h3>
                </td></tr>
                <tr><td class="f">
                    <h3 class="t">
                        <a href="http://www.baidu.com/link?url=fake3">link3</a>
                    </h3>
                </td></tr>
                </table>
            </body>
            </html>
            """

        def fake_parse_href(link):
            if link == "http://www.baidu.com/link?url=fake1":
                return "http://test.com/"
            elif link == "http://www.baidu.com/link?url=fake2":
                return "http://testtest.com/"
            elif link == "http://www.baidu.com/link?url=fake3":
                return "http://www.test.com/"

        self.stubs.Set(self.baidu_scraper, '_get_html', fake_get_html)
        self.stubs.Set(self.baidu_scraper, 'parse_href', fake_parse_href)
        self.baidu_scraper.get_links_task(max_pages=1)
        expected_links = [{'rank': 1, 'url': 'http://test.com/'},
                          {'rank': 3, 'url': 'http://www.test.com/'}]
        links = self.baidu_scraper.redis_conn.smembers(
            self.baidu_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_get_links_task_connection_error(self):
        self.stubs.Set(self.baidu_scraper, 'endpoint', 'http://baidu_blocked/')
        self.baidu_scraper.get_links_task(max_pages=1)
        expected_links = [{'rank': 0,
                           'url': 'DNS error or connection refused'}]
        links = self.baidu_scraper.redis_conn.smembers(
            self.baidu_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_parse_href(self):
        def fake_get(link, allow_redirects):
            response = requests.Response()
            response.headers = {'location': 'http://test.com/'}
            return response
        self.stubs.Set(requests, 'get', fake_get)
        href = 'http://www.baidu.com/link?url=fake'
        expected_url = 'http://test.com/'
        self.assertEqual(expected_url,
                         self.baidu_scraper.parse_href(href))

    def test_parse_href_special_case(self):
        """Sometimes Baidu put direct link in the result and in this case,
        there will be no redirect link
        """
        def fake_get(link, allow_redirects):
            response = requests.Response()
            response.headers = {'location': None}
            return response
        self.stubs.Set(requests, 'get', fake_get)
        href = 'http://test.com/'
        expected_url = 'http://test.com/'
        self.assertEqual(expected_url,
                         self.baidu_scraper.parse_href(href))

    def test_check_link(self):
        link = 'http://www.test.com/test'
        self.assertEqual(True,
                         self.baidu_scraper.check_link(link))

        link = 'http://www.testtest.com/test'
        self.assertEqual(False,
                         self.baidu_scraper.check_link(link))


class BingScraperTest(test.TestCase):

    def setUp(self):
        super(BingScraperTest, self).setUp()
        self.stubs.Set(redis, 'Redis', FakeRedis)
        self.bing_scraper = BingScraper('test', 'test.com')

    def test_get_links_task(self):
        def fake_get_html(page):
            return """
            <html>
            <body>
                <li class="sa_wr">
                    <div class="sb_tlst">
                    <h3>
                        <a href="http://test.com/">link 1</a>
                    </h3>
                    </div>
                </li>
                <li class="sa_wr">
                    <div class="sb_tlst">
                    <h3>
                        <a href="http://testtest.com/">link 2</a>
                    </h3>
                    </div>
                </li>
                <li class="sa_wr">
                    <div class="sb_tlst">
                    <h3>
                        <a href="http://www.test.com/">link 3</a>
                    </h3>
                    </div>
                </li>
            </body>
            </html>
            """
        self.stubs.Set(self.bing_scraper, '_get_html', fake_get_html)
        self.bing_scraper.get_links_task(max_pages=1)

        expected_links = [{'rank': 1, 'url': 'http://test.com/'},
                          {'rank': 3, 'url': 'http://www.test.com/'}]
        links = self.bing_scraper.redis_conn.smembers(
            self.bing_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_get_links_task_connection_error(self):
        self.stubs.Set(self.bing_scraper,
                       'endpoint', 'http://google_blocked/')
        self.bing_scraper.get_links_task(max_pages=1)

        expected_links = [{'rank': 0,
                           'url': 'DNS error or connection refused'}]
        links = self.bing_scraper.redis_conn.smembers(
            self.bing_scraper.scrap_task_result)
        links = [json.loads(link) for link in links]
        if len(links) > 1:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        self.assertEqual(expected_links, links)

    def test_parse_href(self):
        href = 'http://test.com/'
        expected_url = 'http://test.com/'
        self.assertEqual(expected_url,
                         self.bing_scraper.parse_href(href))

    def test_check_link(self):
        link = 'http://www.test.com/test'
        self.assertEqual(True,
                         self.bing_scraper.check_link(link))

        link = 'http://www.testtest.com/test'
        self.assertEqual(False,
                         self.bing_scraper.check_link(link))
