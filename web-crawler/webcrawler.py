import logging
import os
import urllib.parse as urlparse

from flask import Flask, make_response, abort, request, jsonify, render_template

from crawler import Crawler

DEBUG = os.environ['WEBCRAWLER_DEBUG'] if 'WEBCRAWLER_DEBUG' in os.environ else False
logging.getLogger().setLevel(logging.DEBUG if DEBUG else logging.INFO)

MAX_THREADS = int(os.environ['WEBCRAWLER_MAX_THREADS']) if 'WEBCRAWLER_MAX_THREADS' in os.environ else 10

app = Flask(__name__)
app.debug = DEBUG


@app.route("/")
def index():
    return make_response(render_template('index.html'))


@app.route("/crawl", methods=['GET'])
def crawl():
    try:
        depth_limit = int(request.values['depth'])
    except ValueError as e:
        return "Depth parameter must be a number", 400
    except:
        depth_limit = 1

    if 'threads' in request.values:
        try:
            threads = int(request.values['threads'])
            if threads <= 0 or threads > MAX_THREADS:
                raise ValueError
        except ValueError as e:
            return "Threads parameter must be a number between 1 and " + str(MAX_THREADS), 400
    else:
        threads = 1

    logging.debug('Threads: ' + str(threads))

    if 'url' in request.values:
        url = request.values['url']
        parsed_url = urlparse.urlsplit(url)
        if parsed_url.scheme not in ['http', 'https']:
            return "Only http and https protocols are supported", 400
        if parsed_url.netloc == '':
            return "Missing domain", 400
        allowed_domains = [ parsed_url.netloc ]
        crawler = Crawler(allowed_domains, depth_limit, threads)
        crawler.crawl(url)
        return jsonify(**crawler.crawled)
    else:
        return "Missing url parameter", 400
