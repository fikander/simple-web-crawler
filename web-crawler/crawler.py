import logging
import requests
import urllib.parse as urlparse
from mimetypes import MimeTypes
import time

import queue
import threading
from threadsafedict import ThreadSafeDict
from consumer import QueueConsumer


class Crawler:
    """ """
    def __init__(self, allowed_domains, depth_limit, max_threads=4):
        super().__init__()
        self.allowed_domains = allowed_domains
        self.depth_limit = depth_limit
        self.max_threads = max_threads
        self.queue = queue.Queue()
        self.crawled = ThreadSafeDict()
        self.queue_consumers = []


    def crawl(self, url):
        self.queue.put((url, 0))
        for i in range(self.max_threads):
            self.queue_consumers.append(
                QueueConsumer(
                    i, self.queue, self.crawled,
                    self.allowed_domains, self.depth_limit
                )
            )
        for consumer in self.queue_consumers:
            consumer.start()
        # FIXME: work out what the stop condition for threads should be
        time.sleep(10)
        for i in range(self.max_threads):
            self.queue.put((None, 0))

        for consumer in self.queue_consumers:
            consumer.join()
