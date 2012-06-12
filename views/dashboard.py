
import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import models
from perftest.results import GoogleResultData, WptResultData, NoDataError

class DashboardHandler(webapp.RequestHandler):

    def get(self, dashboard="main"):

        t = memcache.get("%s_dashboard_html" % dashboard)

        context = {
            'dashboards': models.Dashboard.all()
        }

        if not t:
            context['results'] = []
            urls = models.Url.all().filter('dashboard =', dashboard).order('-dashboard')
            if urls.count() < 1:
                self.redirect('/dashboard')
            for url in urls:
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

                context['results'].append(result)

            # Cache the template until we flush the cache on new results.
            try:
                logging.debug('trying')
                t = template.render('templates/dashboard/%s.html' % dashboard, context)
            #except TemplateDoesNotExist:
            except:
                t = template.render('templates/dashboard/default.html', context)
            #memcache.set("%s_dashboard_html" % dashboard, t)

        self.response.out.write(t)

