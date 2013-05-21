Scrap Doc
=========
Get the keyword search results that belongs to the domain you want from
search engines such as Google, Baidu, Bing

Production Deployment
---------------------

Clone the repository::

    git clone https://github.com/lanticezdd/scrap

Install::
    
    cd scrap
    ./install

Go to http://your-ip:5000/ and you should see the website

Development
-----------

Install dependencies::

    yum install python-virtualenv redis

Clone the repository::

    git clone https://github.com/lanticezdd/scrap

Create virtual environment::

    cd scrap
    virtualenv .venv
    source .venv/bin/activate
    python setup.py develop

Start services::

    /etc/init.d/redis start
    scrap-api
    scrap-scraper

Running tests::

    nosetests

Architecture
------------


Issues And Improvements
-----------------------

1. For simplicity, the POST in Rest API is put under the actual resource.
   It should be called against http://localhost:5000/search 
   other than http://locahost:5000/search/google:test:test.com

2. Google has rate limiting and this is not currently addressed
