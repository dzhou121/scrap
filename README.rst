Scrap Doc
=========
Get the keyword search results that belongs to the domain you want from
search engines such as Google, Baidu, Bing

Production Deployment
---------------------

Clone the repository::

    $ git clone https://github.com/lanticezdd/scrap

Install::
    
    $ cd scrap
    $ sudo ./install

Go to http://your-ip:5000/ and you should see the website

Note: You can deploy scrap-scraper on multiple machines to increase the performance    

Development
-----------

Install dependencies::

    $ sudo yum install python-devel python-virtualenv python-setuptools libxml2-devel libxslt-devel libevent-devel redis

Clone the repository::

    $ git clone https://github.com/lanticezdd/scrap

Create virtual environment::

    $ cd scrap
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ python setup.py develop

Start services::

    $ sudo /etc/init.d/redis start
    $ scrap-api
    $ scrap-scraper

Running tests::

    $ nosetests

Architecture
------------

::

    HTTP Reqeust 
        |
        |
        |
    scrap-api
        |
        |
        |                 Get results       fetch queue
    scrap.scraper.api.API <---------> Redis -----------> scrap-scraper
                         publish queue  ^                      |
                                        |                      |
                                        |                      |
                                        |                ScraperManager
                                        |                      |
                                        |                      |
                                        |                      |
                                        +---------- Google/Baidu/BingScraper
                                       Store results

The Restful API is provided by scrap-api, and when a HTTP request comes in, it
will call scrap.scraper.api.API to get results from Redis, or publish a new
task to Redis queue.

ScraperManager subscribes Redis pubsub and will consume the new task when there
is a new message. It will call the actual search engine scrapers to do the
searches. The scrapers will download the html from search engines, parse the
results, and store the results to Redis.

Config
------

=============================    =================================================
``MAX_PAGES``                    The max pages in the search engine the scraper
                                 will search.

``CONCURRENCY``                  The concurrency when downloading html from search
                                 engines.

``SCRAPER_MANAGER_CONSUMERS``    The number of consumers that subscribes to Redis
                                 queue at the same time 

``CACHE_DURATION``               The duration that scrap will store the results
                                 in Redis

``LISTEN_IP``                    The listening IP for scrap-api

``LISTEN_PORT``                  The listening port for scrap-api

``REDIS_HOST``                   The Redis host that scrap connects to

``REDIS_PORT``                   The Redis port that scrap connects to

``REDIS_DB``                     The Redis DB that will be used

``REDIS_PW``                     The Redis password will be used
=============================    =================================================

Issues And Improvements
-----------------------

1. Google has a rate limiting and this is not currently addressed.

2. Better configuration control is needed.

3. logging facility is needed.

4. For simplicity, the POST in Rest API is put under the actual resource.
   It should be put under http://localhost:5000/search 
   rather than http://locahost:5000/search/google:test:test.com
