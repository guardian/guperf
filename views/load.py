#!/usr/bin/env python

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import models
from perftest.requests import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from perftest.tests import do_wpt_tests, get_wpt_results, do_google_tests
from utils import get_messages, add_message

class ScheduleHandler(webapp.RequestHandler):

    def get(self, key=None):
        # Schedule all the URLs for test.
        if key:
            urls = [models.Url.get(key)]
        else:
            urls = [model in models.Url.all()]

        for url in urls:
            test = models.UrlTestTask(url=url.url, name=url.name)
            test.put()

        add_message('%s new jobs scheduled' % str(len(urls)))
        add_message('%s total jobs in the queue' % str(models.UrlTestTask.all().count()))

        return self.redirect('/admin/urls')

class JobHandler(webapp.RequestHandler):

    def is_auto(self):
        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True
        return auto

    def get(self):

        urls = models.UrlTestTask.all().order('-dt')
        urls_to_test = urls[:2]

        if (urls.count() > 0):    
            context = {
                'google_results': do_google_tests(urls_to_test, self.is_auto()),
                'wpt_results': do_wpt_tests(urls_to_test, self.is_auto())
            }

            logging.info('%s tests started. %s remaining in queue.' % (len(urls_to_test), urls.count()))

            self.response.out.write('%s new tests started.' % len(urls_to_test))
            self.response.out.write('<br />%s tests remaining in queue.' % urls.count())

            for url in urls:
                url.delete()

        else:
            logging.info('0 tests remaining in queue.')
            self.response.out.write('no tests remaining in queue.')

class ResultsHandler(webapp.RequestHandler):
    def get(self):

        results = get_wpt_results()

        # Just bulk kill the cache.
        memcache.flush_all()

        self.response.out.write('%s results collected.' % len(results))


