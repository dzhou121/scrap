import redis
from scrap import settings
from scrap.scraper import scraper


class ScraperManager(object):
    """ The scraper manager which consums the queue and call the task """

    def __init__(self):
        self.redis_conn = redis.Redis(host=settings.REDIS_HOST,
                                      port=settings.REDIS_PORT,
                                      db=settings.REDIS_DB,
                                      password=settings.REDIS_PW)

    def sub(self):
        """ subscribe to redis pubsub """
        pubsub = self.redis_conn.pubsub()
        pubsub.subscribe(settings.SCRAP_TOPIC)
        for msg in pubsub.listen():
            self.scrap_next()

    def scrap_next(self):
        """ start the scrap task got from the queue """
        task = self.redis_conn.lpop(settings.SCRAP_QUEUE)
        if task is None:
            return

        try:
            search_engine, keyword, domain = task.split(':')
            scraper_class = getattr(scraper,
                                    '%sScraper' % search_engine.capitalize())
        except ValueError:
            print 'wrong queue string'
        except AttributeError:
            print 'wrong search engine name'
        else:
            scraper_obj = scraper_class(keyword, domain)
            scraper_obj.get_links_task()
