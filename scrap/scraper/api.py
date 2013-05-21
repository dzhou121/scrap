import json
import redis
from flask.ext import restful
from scrap import settings


class API(object):
    """ API fro interacting with scraper manager """

    def __init__(self, search_engine, keyword, domain):
        self.redis_conn = redis.Redis(host=settings.REDIS_HOST,
                                      port=settings.REDIS_PORT,
                                      db=settings.REDIS_DB,
                                      password=settings.REDIS_PW)
        self.search_engine = search_engine
        self.keyword = keyword
        self.domain = domain
        params_dict = {
            'search_engine': search_engine,
            'keyword': keyword,
            'domain': domain
        }
        self.scrap_task_status = settings.SCRAP_TASK_STATUS % params_dict
        self.scrap_task_result = settings.SCRAP_TASK_RESULT % params_dict

    def get_links(self):
        """ get the scrap result from Redis """
        if self.get_status() is None:
            restful.abort(404,
                          message='Please create the task '
                                  'before access the result')
        links = self.redis_conn.smembers(self.scrap_task_result)
        links = [json.loads(link) for link in links]
        if links:
            links = [(link['rank'], link['url']) for link in links]
            links.sort()
            links = [{'rank': link[0], 'url': link[1]} for link in links]
        return links

    def get_links_task(self):
        """ Start new scrap task by adding the task to the queue """
        if self.get_status() is not None:
            restful.abort(400,
                          message='The task already exists')
        queue = ':'.join([self.search_engine, self.keyword, self.domain])
        self._add_queue(queue)
        self._notify_sub()

    def get_status(self):
        """ Get the status of the task """
        return self.redis_conn.get(self.scrap_task_status)

    def _add_queue(self, queue):
        """ Add new task to the queue """
        self.redis_conn.rpush(settings.SCRAP_QUEUE, queue)

    def _notify_sub(self):
        """ Notify the subscribers there is new task in the queue """
        self.redis_conn.publish(settings.SCRAP_TOPIC, '1')
