
Simple Web Crawler
==================

Running
-------
As a prerequisite you need Docker machine running and docker-compose installed. Check `docker --version` and ` docker-compose --version` to verify they exist in your setup. This has been tested with Docker 1.10.3 and docker-compose version 1.6.2.

To start Docker container and server on default port 8080 (make sure docker machine is running first first `docker-machine status`):

    git clone git@github.com:fikander/simple-web-crawler.git
    cd simple-web-crawler
    make start

This will build the Docker image if necessary and start it your machine.
On OSX or Windows you can access simple web interface at:

    `docker-machine ip`:8080

(Make sure that port 8080 is available, otherwise edit docker-compose.yml to change it.)

Testing
-------

Run
    make test

to execute unit/integration tests.


Endpoints
---------

    \crawl?url=URL_TO_START_CRAWLING

This will crawl this page and recursively follow all the links from it while staying within the domain.
Returns JSON results.
Example:

    curl "`docker-machine ip`:8080/crawl?depth=1&url=http://google.com"

Note, that it will usually take long time to crawl anything with depth > 1.

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
