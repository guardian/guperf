
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import models
from perftest.results import GoogleResultData, WptResultData, NoDataError

class DashboardHandler(webapp.RequestHandler):

    def get(self):

        t = memcache.get("dashboard_html")
        if not t:

            results = []
            for url in models.Url.all().order('-dashboard'):
                logging.debug(url.url)
                try:
                    result = {
                        'google': GoogleResultData(url.url),
                        'wpt': WptResultData(url.url),
                        'name': url.name,
                        'url': url.url
                    }

                except NoDataError:
                    logging.info("There are no full results yet for %s" % url.url)
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
            for url in models.Url.all().filter('dashboard =', 'beta'):
                logging.debug(url.url)
                try:
                    result = {
                        'google': GoogleResultData(url.url),
                        'wpt': WptResultData(url.url),
                        'name': url.name,
                        'url': url.url
                    }

                except NoDataError:
                    logging.info("There are no full results yet for %s" % url.url)
                    continue

                results.append(result)

            # Cache the template until we flush the cache on new results.
            t = template.render('templates/beta_dashboard.html', {'results': results})
            memcache.set("beta_dashboard_html", t)

        self.response.out.write(t)

