MAX_PAGES = 20
CONCURRENCY = 20
SCRAPER_MANAGER_CONSUMERS = 10
CACHE_DURATION = 86400

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 5000

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PW = None

SCRAP_QUEUE = 'scrap:queue'
SCRAP_TOPIC = 'scrap:topic'
SCRAP_TASK_STATUS = 'scrap:%(search_engine)s:%(keyword)s:%(domain)s:status'
SCRAP_TASK_RESULT = 'scrap:%(search_engine)s:%(keyword)s:%(domain)s:result'
