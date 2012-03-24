
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import models
from utils import xml_to_json, get_urls
from perftest.results import GoogleResultData, WptResultData, NoDataError

class DashboardHandler(webapp.RequestHandler):

    def get_test_results(self, provider, url):
    	return models.TestResult.all().filter('url =', url).filter('provider =', provider).filter('results_received', True).order('-dt')

    def get(self):
        urls = get_urls()
        context = {
            'results': []
        }
        
        for url in urls:
            try:
                result = {
                    'google': GoogleResultData(url),
                    'wpt': WptResultData(url)
                }
            except NoDataError:
                logging.info("There are no full results yet for %s" % url)
                continue

            context['results'].append(result)

        self.response.out.write(template.render('templates/dashboard.html', context))