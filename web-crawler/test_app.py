import pytest
import webcrawler
import responses
import requests
import json
import urllib.parse as urlparse

@pytest.yield_fixture(scope="session")
def client(request):
	webcrawler.app.config['TESTING'] = True
	client = webcrawler.app.test_client()
	with webcrawler.app.app_context():
		# TODO: any db init code
		pass
	responses.add(
		responses.GET, 'http://test.me/circular1',
		body='''
		<html><body>
			<a href="/circular2"/>
			<a href="/circular1"/>
		</body></html>
		''', status=200
	)
	responses.add(
		responses.GET, 'http://test.me/circular2',
		body='''
		<html><body><a href="/circular1"/></body></html>
		''', status=200
	)

	responses.add(
		responses.GET, 'https://test.me/https',
		body='''
		<a href="http://test.me/http">
		''', status=200
	)
	responses.add(
		responses.GET, 'http://test.me/http',
		body='''
		<a href="http://external.com">
		''', status=200
	)
	yield client
	# TODO: any teardown code


def test_index_page(client):
	rv = client.get("/")
	assert(rv.status_code == 200)


def crawl(client, url):
	rv = client.get("/crawl?" + urlparse.urlencode([('url', url)]))
	if rv.status_code == 200:
		resp = json.loads(rv.data.decode())
	else:
		resp = None
	return rv, resp


def test_weird_scheme(client):
	rv, resp = crawl(client, 'weird://scheme')
	assert(rv.status_code == 400)


@responses.activate
def test_circular_links(client):
	rv, resp = crawl(client, 'http://test.me/circular1')
	assert('http://test.me/circular1' in resp)
	assert('http://test.me/circular2' in resp)
	assert(len(resp.keys()) == 2)


@responses.activate
def test_http_https_redirection(client):
	# TODO: Mock https connection to enable test 
	# rv, resp = crawl(client, 'https://test.me/https')
	# assert('http://external.com' in resp)
	pass


@responses.activate
def test_local_and_relative_links(client):

	responses.add(
		responses.GET, 'http://test.me/local',
		body='''
		<a href="local1"/>
		<a href="path/local2"/>
		<a href="path/../relative/local3/"/>
		''', status=200
	)
	responses.add(
		responses.GET, 'http://test.me/local1',
		body='''
		''', status=200
	)
	responses.add(
		responses.GET, 'http://test.me/path/local2',
		body='''
		''', status=200
	)
	responses.add(
		responses.GET, 'http://test.me/path/../relative/local3',
		body='''
		''', status=200
	)

	rv, resp = crawl(client, 'http://test.me/local')
	assert('http://test.me/local1' in resp)
	assert('http://test.me/path/local2' in resp)
	assert('http://test.me/relative/local3' in resp)


@responses.activate
def test_weird_hrefs(client):
	responses.add(
		responses.GET, 'http://test.me/weird_href',
		body='''
		<a href="weird stuff">
		''', status=200
	)
	rv, resp = crawl(client, 'http://test.me/weird_href')
	assert(resp['http://test.me/weird stuff']['type'] is None)


@responses.activate
def test_nonexisting_links(client):
	responses.add(
		responses.GET, 'http://test.me/404',
		body='''
		<a href="http://test.me/nonexisting">
		''', status=200
	)

	rv, resp = crawl(client, 'http://test.me/404')
	assert('http://test.me/404' in resp)
	assert(resp['http://test.me/nonexisting']['type'] is None)


@responses.activate
def test_images(client):
	responses.add(
		responses.GET, 'http://test.me/images',
		body='''
		<img src="img1.gif">
		<img src="img2.jpeg">
		''', status=200
	)

	rv, resp = crawl(client, 'http://test.me/images')
	assert('http://test.me/img1.gif' in resp)
	assert(resp['http://test.me/img1.gif']['type'] == 'image/gif')
	assert(len(resp.keys()) == 3)
