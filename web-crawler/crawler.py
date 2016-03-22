import logging
import queue
import threading
from threadsafedict import ThreadSafeDict
from consumer import QueueConsumer


class Crawler:
    """ Spawns threads, inititates work queue and waits for it to get empty
    """
    def __init__(self, allowed_domains, depth_limit, max_threads=4):
        super().__init__()
        self.allowed_domains = allowed_domains
        self.depth_limit = depth_limit
        self.max_threads = max_threads
        self.queue = queue.Queue()
        self.crawled = ThreadSafeDict()
        self.queue_consumers = []


    def crawl(self, url):
        self.queue.put((url, 0))  # queue contains tuples of (URL, depth)
        for i in range(self.max_threads):
            self.queue_consumers.append(
                QueueConsumer(
                    self.queue, self.crawled,
                    self.allowed_domains, self.depth_limit
                )
            )
        for consumer in self.queue_consumers:
            consumer.start()
        # wait for queue and terminate all threads
        self.queue.join()
        for i in range(self.max_threads):
            self.queue.put((None, 0))
        for consumer in self.queue_consumers:
            consumer.join()
