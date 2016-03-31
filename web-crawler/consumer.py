import threading
import time
import logging
import queue
import requests
import urllib.parse as urlparse

from bs4 import BeautifulSoup


class QueueConsumer(threading.Thread):
    """Processes queue of urls which updating dict of crawled urls.
    """

    _followable_content_types = (
        None,
        'text/html',
        'text/plain'
    )

    def __init__(self, queue, crawled, allowed_domains, depth_limit):
        super().__init__(daemon=True)
        self.queue = queue
        self.crawled = crawled
        self.allowed_domains = allowed_domains
        self.depth_limit = depth_limit
        self.count = 0


    def run(self):
        while True:
            try:
                logging.debug(self.name + ': awaiting next item...')
                url, depth = self.queue.get()
                if url is None:
                    logging.debug(self.name + ': exiting')
                    break
            except queue.Empty:
                logging.debug(self.name + ': nothing to work on - exiting')
                break
            self._process(url, depth)
            self.count += 1
            self.queue.task_done()


    def _process(self, url, depth):
        follow, base_url = self._qualify_link(url)
        if follow:
            logging.debug('following ' + url)
            content_type = None
            try:
                r = requests.get(url)
                if 'content-type' in r.headers:
                    content_type = r.headers['content-type'].split(';')[0]
                with self.crawled as c:
                    c[url] = {
                        'outlinks': dict(),  # will remain empty for external pages
                        'type': content_type
                    }
                if content_type in QueueConsumer._followable_content_types:
                    self._parse_content(url, r.text, base_url, depth)
                else:
                    logging.debug('NOT parsing this content-type: ' + content_type)
            except requests.exceptions.RequestException as e:
                with self.crawled as c:
                    c[url] = {
                        'outlinks': dict(),
                        'type': content_type
                    }
                logging.debug('Connection error: ' + str(e))
        else:
            with self.crawled as c:
                c[url] = {
                    'outlinks': dict()  # will remain empty for external pages
                }
            logging.debug('NOT following ' + url)


    def _parse_content(self, url, content, base_url, depth):
        """Extract all the links and media and add them to links queue.
        TODO: Perform any extra processing on the content, e.g. indexing.
        """
        logging.debug("Parsing " + url + " depth: " + str(depth))
        # find all links
        # TODO: be more intelligent with guessing content type - assuming html5 at the moment
        soup = BeautifulSoup(content, 'html5lib')

        # collect all relevant urls
        outlinks = []
        for a in soup.findAll('a'):
            outlinks.append(self._normalise_url(base_url, a.get('href')))
        for i in soup.findAll('img'):
            outlinks.append(self._normalise_url(base_url, i.get('src')))

        with self.crawled as c:
            for outlink in outlinks:
                # update outlinks for this url
                outlinks_list = c[url]['outlinks']
                if outlink in outlinks_list:
                    outlinks_list[outlink] += 1
                else:
                    outlinks_list[outlink] = 1
                # only add to queue if not already crawled
                if (depth < self.depth_limit and
                        outlink not in self.crawled):
                    self.queue.put((outlink, depth + 1))


    def _qualify_link(self, url):
        """Decide what link this is and whether it should be followed.
        Returns (follow, content_type), where content_type is None for unknown
        """
        parsed_url = urlparse.urlsplit(url)
        base_url = '{u.scheme}://{u.netloc}/'.format(u=parsed_url)
        with self.crawled as c:
            follow = (parsed_url.netloc in self.allowed_domains and
                    url not in c)
        return follow, base_url


    def _normalise_url(self, base_url, url):
        """Strip GET parameters. Turn local links into absolute ones using base_url.
        """
        parsed_url = urlparse.urlsplit(urlparse.urljoin(base_url, url))
        url = '{u.scheme}://{u.netloc}{u.path}'.format(u=parsed_url)
        if url[-1] == '/':
            url = url[:-1]
        return url
