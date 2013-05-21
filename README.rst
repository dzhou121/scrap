Scrap Doc
=========

Production Deployment
---------------------

For CentOS, Redhat
Install dependencies::

    yum install libevent-devel

Issues And Improvements
-----------------------

For simplicity, the POST in Rest API is put under the actual resource. It
should be called against http://localhost:5000/search other than
http://locahost:5000/search/google:test:test.com
