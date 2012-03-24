
import logging
import os
import yaml

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

import models
from utils import xml_to_json, get_urls
from testresult import GoogleResultData, WptResultData, NoDataError

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

        path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
        self.response.out.write(template.render(path, context))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/', DashboardHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()