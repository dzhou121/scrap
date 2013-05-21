from flask.ext import restful
from scrap.scraper import api


class API(restful.Resource):
    """ restful resource for scraper API """

    def __init__(self):
        super(API, self).__init__()

    def get(self, params):
        """ get the scrap result """
        search_engine, keyword, domain = self._get_params(params)
        scraper_api = api.API(search_engine, keyword, domain)
        links = scraper_api.get_links()
        return {'links': links}

    def post(self, params):
        """ Start the scrap task """
        search_engine, keyword, domain = self._get_params(params)
        scraper_api = api.API(search_engine, keyword, domain)
        scraper_api.get_links_task()
        return '', 202

    def put(self, params):
        """ get the scrap task status """
        search_engine, keyword, domain = self._get_params(params)
        scraper_api = api.API(search_engine, keyword, domain)
        status = scraper_api.get_status()
        return {'status': status}

    def _get_params(self, params):
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

        return (search_engine, keyword, domain)
