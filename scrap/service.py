import gevent

from gevent.wsgi import WSGIServer
from scrap import settings
from scrap.scraper import manager
from scrap.wsgi import app


class ScraperService(object):
    """ the service for starting the scraper manager """

    def __init__(self):
        pass

    def start(self):
        """ use gevent to spawn multiple managers that can
        consume the queue simultaneously
        """
        consumers = [gevent.spawn(self._start)
                     for i in xrange(settings.SCRAPER_MANAGER_CONSUMERS)]
        gevent.joinall(consumers)

    def _start(self):
        """ start the manager subscriber """
        scraper_manager = manager.ScraperManager()
        scraper_manager.sub()


class WSGIService(object):
    """ The service for serving the Restful API """

    def __init__(self):
        self.app = app
        self.host = settings.LISTEN_IP
        self.port = settings.LISTEN_PORT

    def start(self):
        """ start the gevent wsgi server """
        server = WSGIServer((self.host, self.port), self.app)
        server.serve_forever()
