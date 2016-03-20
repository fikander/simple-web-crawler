
Simple Web Crawler
==================

What it is
----------

It's a Dockerised web service exposing an endpoint which crawls http/https pages and builds a site map containing all visited links, outgoing links within them, as well as MIME type for each link.
It stays within the domain, but does provide information about all links going outside of the domain.

There's also a simple UI providing convenience method for using the endpoint.


Running
-------
As a prerequisite you need Docker machine running and docker-compose installed. Check `docker --version` and ` docker-compose --version` to verify they exist in your setup. This has been tested with Docker 1.10.3 and docker-compose version 1.6.2.

To start Docker container and server on default port 8080 (make sure docker machine is running first first `docker-machine status`):

    git clone git@github.com:fikander/simple-web-crawler.git
    cd simple-web-crawler
    make start

This will build the Docker image if necessary and start it.

By default logs Docker volume is mounted at `~/logs/simple-web-crawler` (as defined in docker-compose.yml). To view server log use `tail -f ~/logs/simple-web-crawler/serverl.log`

To stop the container:

    make stop

Testing
-------

Run
    make test

to execute unit/integration tests.


Endpoints
---------

    \crawl?url=URL_TO_START_CRAWLING

This will crawl URL_TO_START_CRAWLING page and recursively follow all the links from it while staying within the domain.
Returns JSON results.
Example:

    curl "`docker-machine ip`:8080/crawl?depth=1&url=http://google.com"

Note, that it will usually take long time to crawl anything with depth > 1.

GUI
---

On OSX or Windows you can access simple web interface at:

    `docker-machine ip`:8080

(Make sure that port 8080 is available, otherwise edit docker-compose.yml to change it.)


Problems, todos and tradeoffs
-----------------------------

- generate documentation
- performance: handle GET parameters better, allow their configuration (url params are stripped at the momement)
- performance: multithreading
- configuration: depth limit
- scale: microservices architecture with threaded queue consumers 
- ui: use React and websockets to get live feedback while crawling
- performance: check for sitemap.xml and parse that first
(should be simple
    for url in BeautifulSoup(data).findAll("loc"):
        print url.text
)
- allow deploying to Amazon AWS
- qa: more exhaustive unit tests
- handle GET parameters. They're ignored at the moment.
