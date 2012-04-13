import logging
import os
import time

from google.appengine.ext import webapp
from django.utils import simplejson as json

import models
from utils import get_urls
from perftest.results import GoogleResultData, WptResultData, NoDataError

class StatusHandler(webapp.RequestHandler):

    def get(self):

        response = {
        	"application": "guperf",
			"time": int(round(time.time() * 1000)),
			"metrics": []
		}

        for url in get_urls():
            try:
            	#google = GoogleResultData(url, 1)
                wpt = WptResultData(url, 1)
                response['metrics'].extend(
                	self.build_metric_json(
                		url,
                		wpt.current.result['data']['median']['firstView']['loadTime'],
                		wpt.current.result['data']['median']['repeatView']['loadTime'],
                		wpt.current.result['data']['median']['firstView']['render'],
                		wpt.current.result['data']['median']['repeatView']['render']
                	)
                )

            except NoDataError:
                logging.info("There are no full results yet for %s" % url)
                continue


        self.response.out.write(json.dumps(response))

    def build_metric_json(self, url, plt1, plt2, render1, render2):

    	return [
				{
					"group": url,
					"name": "plt1",
					"type": "gauge",
					"title": "Page Load Time 1",
					"description": "Total time for all assets to load with empty cache",
					"value": plt1
				},
				{
					"group": url,
					"name": "plt2",
					"type": "gauge",
					"title": "Page Load Time 2",
					"description": "Total time for all assets to load with primed cache",
					"value": plt2
				},
				{
					"group": url,
					"name": "render1",
					"type": "gauge",
					"title": "Render 1",
					"description": "Total time for core content to render with empty cache",
					"value": render1
				},
				{
					"group": url,
					"name": "render2",
					"type": "gauge",
					"title": "Render 2",
					"description": "Total time for core content to render with primed cache",
					"value": render2
				}
			]