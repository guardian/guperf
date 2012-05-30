
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import models
from utils import get_urls, get_beta_urls
from perftest.results import GoogleResultData, WptResultData, NoDataError

class DashboardHandler(webapp.RequestHandler):

    def get(self):

        t = memcache.get("dashboard_html")
        if not t:

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

            # Cache the template until we flush the cache on new results.
            t = template.render('templates/dashboard.html', {'results': results})
            memcache.set("dashboard_html", t)

        self.response.out.write(t)

class BetaDashboardHandler(webapp.RequestHandler):

    def get(self):

        t = memcache.get("beta_dashboard_html")
        if not t:

            results = []
            for url in get_beta_urls():
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

            # Cache the template until we flush the cache on new results.
            t = template.render('templates/beta_dashboard.html', {'results': results})
            memcache.set("beta_dashboard_html", t)

        self.response.out.write(t)

