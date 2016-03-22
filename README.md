
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

By default logs Docker volume is mounted at `~/logs/simple-web-crawler` (as defined in docker-compose.yml). To view server log use

    tail -f ~/logs/simple-web-crawler/server.log

To stop the web service:

    make stop

Testing
-------

Run:

    make test

to execute unit/integration tests.


Endpoints
---------

    /crawl?threads=THREADS_COUNT&depth=MAX_DEPTH&url=URL_TO_START_CRAWLING

- `URL_TO_START_CRAWLING` crawl starting with this URL, recursively follow all the links from it while staying within the domain.
- `THREADS_COUNT` is number of worker threads per request (1 by default). `WEBCRAWLER_MAX_THREADS` environment variable limits max number of threads.
- `MAX_DEPTH` is the crawling depth (1 by default). Value of 0 will not follow any links. 

Returns JSON results.

Example:

    curl "`docker-machine ip`:8080/crawl?threads=4&depth=1&url=http://google.com"

Note, that it will usually take long time to crawl anything with depth > 1.

GUI
---

On OSX or Windows you can access simple web interface at:

    `docker-machine ip`:8080

(Make sure that port 8080 is available, otherwise edit `docker-compose.yml` to change it.)


Problems, todos and tradeoffs
-----------------------------

- performance: handle GET parameters better, allow their configuration (url params are stripped at the momement)
- performance: multithreading
- performance: do not block on `/crawl` request. Return immediately and start job in the background. Crawling can take hours.
- scale: microservices architecture with threaded queue consumers
- ui: use React and websockets to get live feedback while crawling
- performance: check for sitemap.xml and parse that first
(should be simple
    for url in BeautifulSoup(data).findAll("loc"):
        print url.text
)
- qa: more exhaustive unit tests
- qa: generate documentation
- deploy: allow deploying to Amazon AWS. `make deploy` doesn't do that and runs non debug version locally instead
