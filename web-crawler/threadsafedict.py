import threading

class ThreadSafeDict(dict):
    """Usage:
    tsd = ThreadSafeDict()
    with tsd as t:
        t[0] = 'foo'
    """
    def __init__(self, *p_arg, **n_arg):
        dict.__init__(self, *p_arg, **n_arg)
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self._lock.release()
