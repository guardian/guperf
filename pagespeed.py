import logging
import json
import yaml
import os

from google.appengine.api import urlfetch

# TODO: Move to config.
g_api_key = "AIzaSyAjyFYyl2LF107vTUyszMx0nNdtkSrQwHQ"
g_url = "https://www.googleapis.com/pagespeedonline/v1/runPagespeed"
url_to_test = "http://www.guardian.co.uk"



class PageSpeedRequest(object):

	def __init__(self, url_to_test):

		url =  "%s?url=%s&key=%s" % (g_url, url_to_test, g_api_key)

		self.rpc = urlfetch.create_rpc(deadline=20)
		urlfetch.make_fetch_call(self.rpc, url);

	
	def get_result(self):

		response = self.rpc.get_result()
		if response.status_code == 200:
			return json.loads(response.content)
		else:
			logging.debug("Not HTTP 200")


def get_results():

	urls = yaml.load(open('urls_to_test.yaml','r').read())

	logging.debug(urls)

	requests = []
	results = []

	for url in urls:
		request = PageSpeedRequest(url)
		requests.append(request)

	for request in requests:
		result = request.get_result()
		results.append(result)

	return results

