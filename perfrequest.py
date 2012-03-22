import logging
import os

from google.appengine.api import urlfetch
from django.utils import simplejson as json
from xml.dom import minidom

import settings


class PerfRequest(object):

	def __init__(self, url_to_test=None):

		if url_to_test:
			self.url_to_test = url_to_test

		url = self.build_url()

		self.rpc = urlfetch.create_rpc(deadline=20) # 20s timeout, pagespeed API can take a little while.
		urlfetch.make_fetch_call(self.rpc, url)

	def build_url(self):
		# Must be implemented by subclass.
		pass

	def parse_response(self, response):
		return minidom.parseString(response.content)

	def get_response(self):
		# TODO: catch exceptions.
		response = self.rpc.get_result()
		if response.status_code == 200:
			return self.parse_response(response)
		else:
			logging.debug("Not HTTP 200")




class GooglePerfRequest(PerfRequest):

	def build_url(self):
		return "%s?url=%s&key=%s&locale=en_GB" % (settings.google_url, self.url_to_test, settings.google_api_key)

	def parse_response(self, response):
		return json.loads(response.content)


class WptTestRunRequest(PerfRequest):

	def build_url(self):

		return '%s?url=%s&k=%s&private=1&f=xml&runs=5&location=London_Chrome.DSL' % (settings.wpt_url, self.url_to_test, settings.wpt_api_key)
		#return 'http://localhost:8888/runtest.xml'


class WptTestResultsRequest(PerfRequest):

	def __init__(self, test_id):

		self.test_id = test_id
		super(WptTestResultsRequest, self).__init__()

	def build_url(self):

		return '%s/%s/' % (settings.wpt_results_url, self.test_id)
		#return 'http://localhost:8888/101110_BCKV/result.xml'

