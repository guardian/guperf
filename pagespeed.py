import logging
import json
import os

from google.appengine.api import urlfetch

import settings

class PageSpeedRequest(object):

	def __init__(self, url_to_test):

		url =  "%s?url=%s&key=%s" % (settings.google_pagespeed_url, url_to_test, settings.google_api_key)

		self.rpc = urlfetch.create_rpc(deadline=20) # 20s timeout, pagespeed API can take a little while.
		urlfetch.make_fetch_call(self.rpc, url)

	
	def get_result(self):
		# TODO: catch exceptions.
		response = self.rpc.get_result()
		if response.status_code == 200:
			return json.loads(response.content)
		else:
			logging.debug("Not HTTP 200")

