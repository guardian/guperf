#!/usr/bin/env python

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import models
from perftest.requests import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from perftest.tests import do_wpt_tests, get_wpt_results, do_google_tests

class LoadHandler(webapp.RequestHandler):

    def is_auto(self):
        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True
        return auto

    def get(self):

        urls = models.Url.all()
        
        context = {
            'google_results': do_google_tests(urls, self.is_auto()),
            'wpt_results': do_wpt_tests(urls, self.is_auto())
        }

        self.response.out.write(template.render('templates/loaded.html', context))

class CompetitorLoadHandler(LoadHandler):

    def get(self):

        urls = get_competitor_urls()
        
        context = {
            'google_results': do_google_tests(urls, self.is_auto()),
            'wpt_results': do_wpt_tests(urls, self.is_auto())
        }

        self.response.out.write(template.render('templates/loaded.html', context))

class LogHandler(webapp.RequestHandler):
    def get(self):

        context = {
            'tests': models.TestResult.all().order('-dt')[0:100]
        }

        self.response.out.write(template.render('templates/log.html', context))

class ResultsHandler(webapp.RequestHandler):
    def get(self):

        results = get_wpt_results()

        # Just bulk kill the cache.
        memcache.flush_all()

        self.response.out.write("Worked" + str(dir(results)))