from flask.ext import restful
from scrap.scraper import api


def check_params(f):
    """ decorator to check the params first """
    def wrapper(self, params):
        try:
            search_engine, keyword, domain = params.split(':')
        except ValueError:
            restful.abort(400, message='Wrong params provided')

        if not keyword:
            restful.abort(400, message='Put provide the keyword')
        elif not domain:
            restful.abort(400, message='Put provide the domain')
        elif not search_engine:
            restful.abort(400, message='Put provide the search engine')
        # TODO probably needs better detection for available search engines
        elif search_engine not in ['google', 'baidu', 'bing']:
            restful.abort(400,
                          message='search engine not google, baidu or bing')

        return f(self, search_engine, keyword, domain)

    return wrapper


class API(restful.Resource):
    """ restful resource for scraper API """

    def __init__(self):
        super(API, self).__init__()

    @check_params
    def get(self, search_engine, keyword, domain):
        """ get the scrap result """
        scraper_api = api.API(search_engine, keyword, domain)
        links = scraper_api.get_links()
        return {'links': links}

    @check_params
    def post(self, search_engine, keyword, domain):
        """ Start the scrap task """
        scraper_api = api.API(search_engine, keyword, domain)
        scraper_api.get_links_task()
        return '', 202

    @check_params
    def put(self, search_engine, keyword, domain):
        """ get the scrap task status """
        scraper_api = api.API(search_engine, keyword, domain)
        status = scraper_api.get_status()
        return {'status': status}
