import logging
import os
import re
import urllib.parse as urlparse
import requests
from mimetypes import MimeTypes

from flask import Flask, make_response, abort, request, jsonify, render_template
from bs4 import BeautifulSoup

DEBUG = os.environ['WEBCRAWLER_DEBUG'] if 'WEBCRAWLER_DEBUG' in os.environ else None
logging.getLogger().setLevel(logging.DEBUG if DEBUG else logging.INFO)

app = Flask(__name__)
app.debug = DEBUG


@app.route("/")
def index():
    return make_response(render_template('index.html', hello='Hello World!'))


@app.route("/crawl", methods=['GET'])
def crawl():
    try:
        depth_limit = int(request.values['depth'])
    except ValueError as e:
        return "Depth parameter must be a number", 400
    except:
        depth_limit = 1

    if 'url' in request.values:
        url = request.values['url']
        parsed_url = urlparse.urlsplit(url)
        if parsed_url.scheme not in ['http', 'https']:
            return "Only http and https protocols are supported", 400
        if parsed_url.netloc == '':
            return "Missing domain", 400
        allowed_domains = [ parsed_url.netloc ]
        crawler = Crawler(allowed_domains, depth_limit)
        crawler.crawl(url)
        return jsonify(**crawler.crawled)
    else:
        return "Missing url parameter", 400


class Crawler:
    """Main crawler class.
    Takes care of queue of links to follow as well as information about already crawled ones.
    """

    _followable_content_types = (
        None,
        'text/html',
        'text/plain',
        'application/x-msdos-program'
    )


    def __init__(self, allowed_domains, depth_limit=1):
        super().__init__()
        self.allowed_domains = allowed_domains
        # allow local links
        self.allowed_domains.append('')
        self.mime = MimeTypes()
        # Queue implemented as dict as we need to store depth data alongside url
        self.queue = dict()  # { url: depth, .. }
        # TODO: make crawled a class
        self.crawled = dict()  # { url: {type: type, outlinks: {link: count, ..}}, .. }
        self.depth_limit = depth_limit


    def crawl(self, url, depth_limit = None):
        """Initiate crawling
        """
        if depth_limit:
            self.depth_limit = depth_limit
        self.queue[url] = 0
        self._consume_queue()


    def _qualify_link(self, url):
        """Decide what link this is and whether it should be followed.
        Returns (follow, content_type), where content_type is None for unknown
        """
        content_type, encoding = self.mime.guess_type(url)
        parsed_url = urlparse.urlsplit(url)
        base_url = '{u.scheme}://{u.netloc}/'.format(u=parsed_url)
        follow = (content_type in self._followable_content_types and
                    parsed_url.netloc in self.allowed_domains and
                    url not in self.crawled)
        return follow, base_url, content_type


    def _normalise_url(self, base_url, url):
        """Strip GET parameters. Turn local links into absolute ones using base_url.
        """
        parsed_url = urlparse.urlsplit(urlparse.urljoin(base_url, url))
        url = '{u.scheme}://{u.netloc}{u.path}'.format(u=parsed_url)
        if url[-1] == '/':
            url = url[:-1]
        return url


    def _consume_queue(self):
        """Take links from queue and parse them
        """
        while len(self.queue) > 0:
            # fetch the next item from the queue and remove it from there
            url = next(iter(self.queue))
            depth = self.queue[url]
            del self.queue[url]

            follow, base_url, content_type = self._qualify_link(url)
            # initialise new crawled link with content_type being just a guess at this point
            assert(url not in self.crawled)
            self.crawled[url] = {
                'type': content_type,
                'outlinks': dict()  # will remain empty for external pages
            }
            if follow:
                logging.debug('following ' + url)
                try:
                    r = requests.get(url)
                    if 'content-type' in r.headers:
                        content_type = r.headers['content-type'].split(';')[0]
                        # update content-type based on actual headers
                        self.crawled[url]['type'] = content_type
                    self._parse_content(url, r.text, base_url, content_type, depth)
                except requests.exceptions.RequestException as e:
                    logging.debug('Connection error: ' + str(e))
            else:
                logging.debug('NOT following ' + url)


    def _parse_content(self, url, content, base_url, content_type, depth):
        """Extract all the links and media and add them to links queue.
        TODO: Perform any extra processing on the content, e.g. indexing.
        """
        if content_type in self._followable_content_types:
            # find all links
            # TODO: be more intelligent with guessing content type - assuming html5 at the moment
            soup = BeautifulSoup(content, 'html5lib')

            # collect all relevant urls
            outlinks = []
            for a in soup.findAll('a'):
                outlinks.append(self._normalise_url(base_url, a.get('href')))
            for i in soup.findAll('img'):
                outlinks.append(self._normalise_url(base_url, i.get('src')))

            for outlink in outlinks:
                # update outlinks for this url
                outlinks_list = self.crawled[url]['outlinks']
                if outlink in outlinks_list:
                    outlinks_list[outlink] += 1
                else:
                    outlinks_list[outlink] = 1
                # only add to queue if not already crawled
                if (depth < self.depth_limit and
                        outlink not in self.crawled and
                        outlink not in self.queue):
                    self.queue[outlink] = depth + 1
        else:
            logging.debug('Dont understand content type: ' + content_type)
