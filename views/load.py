#!/usr/bin/env python

import logging
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

import models
from perftest.requests import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from utils import get_urls

class LoadHandler(webapp.RequestHandler):

    def is_auto(self):
        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True
        return auto

    def do_wpt_tests(self, urls):

        auto = self.is_auto()
        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for url in urls:
            logging.info("Making wpt testrun request for %s" % url)
            requests[url] = WptTestRunRequest(urls[url])

        pass

        for url in requests:
            result = {}
            xml = requests[url].get_response()
            if result is not None:

                testrun = models.TestResult(
                    provider = 'wpt',
                    url = url,
                    dt = datetime.datetime.now(),
                    auto = auto,
                    results_received = False,
                    provider_id = xml.getElementsByTagName('testId')[0].childNodes[0].data,
                    # Store the XML. You never know.
                    result = xml.toxml())
                testrun.put()

                results.append(result)

        return results

    def do_google_tests(self, urls):

        auto = self.is_auto()
        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for url in urls:
            logging.info("Making google request for %s" % url)
            requests[url] = GooglePerfRequest(urls[url])

        for url in requests:
            result = requests[url].get_response()
            if result is not None:
                result['name'] = url

                pageload = models.TestResult(
                    provider = 'google',
                    url = url,
                    dt = datetime.datetime.now(),
                    auto = auto,
                    results_received = True,
                    # Store the results as JSON, rather than on model fields.
                    result = json.dumps(result))
                pageload.put()

                results.append(result)

        return results

    def get(self):

        urls = get_urls()
        
        context = {
            'google_results': self.do_google_tests(urls),
            'wpt_results': self.do_wpt_tests(urls)
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

        unfulfilled_test_runs = models.TestResult.all().filter('results_received =', False).filter('provider =' ,'wpt')

        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for test in unfulfilled_test_runs:
            logging.info("Making wpt results request for %s" % test.url)
            requests[test.url] = WptTestResultsRequest(test.provider_id)

        for url in requests:
            xml = requests[url].get_response()
            if xml is not None:
                if xml.getElementsByTagName('statusCode')[0].childNodes[0].data == '200':
                    unfulfilled_test_runs = models.TestResult.all().filter('results_received =', False).filter('provider =' ,'wpt')
                    testrun = unfulfilled_test_runs.filter('url =', url).fetch(1)[0]
                    testrun.result = xml.toxml()
                    testrun.results_received = True
                    testrun.put()
                    results.append(testrun)
            else:
                logging.info("We tried to get results for %s, but no go." % url)

        self.response.out.write("Worked" + str(dir(results)))