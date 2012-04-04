#!/usr/bin/env python

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import models
from perftest.requests import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from perftest.tests import do_wpt_tests, get_wpt_results, do_google_tests
from utils import get_urls, get_competitor_urls

class LoadHandler(webapp.RequestHandler):

    def is_auto(self):
        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True
        return auto

    def get(self):

        urls = get_urls()
        
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

        self.response.out.write("Worked" + str(dir(results)))