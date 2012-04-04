
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import models
from utils import get_urls
from perftest.results import GoogleResultData, WptResultData, NoDataError

class DashboardHandler(webapp.RequestHandler):

    def get(self):

        results = []
        for url in get_urls():
            logging.debug(url)
            try:
                result = {
                    'google': GoogleResultData(url),
                    'wpt': WptResultData(url)
                }
            except NoDataError:
                logging.info("There are no full results yet for %s" % url)
                continue

            results.append(result)

        self.response.out.write(template.render('templates/dashboard.html', {'results': results}))