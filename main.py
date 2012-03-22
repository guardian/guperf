#!/usr/bin/env python

import logging
import os
import yaml
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

import models
from perfrequest import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from utils import OrderedDictYAMLLoader

class LoadHandler(webapp.RequestHandler):

    def get(self):

        urls = yaml.load(open('urls_to_test.yaml','r').read(), OrderedDictYAMLLoader)
        
        context = {
            'google_results': self.do_google_tests(urls),
            'wpt_results': self.do_wpt_tests(urls)
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/loaded.html')
        self.response.out.write(template.render(path, context))

    def do_wpt_tests(self, urls):

        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True

        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for id in urls:
            requests[id] = WptTestRunRequest(urls[id])

        pass

        for id in requests:
            result = {}
            xml = requests[id].get_response()
            if result is not None:

                testrun = models.WptTestRun(
                    id=id,
                    dt=datetime.datetime.now(),
                    auto=auto,
                    results_received = False,
                    test_id=xml.getElementsByTagName('testId')[0].childNodes[0].data,
                    # Store the XML. You never know.
                    result=xml.toxml())
                testrun.put()

                results.append(result)

        return results

    def do_google_tests(self, urls):

        auto = self.request.get('auto', False)
        if auto is not False:
            auto = True

        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for id in urls:
            requests[id] = GooglePerfRequest(urls[id])

        for id in requests:
            result = requests[id].get_response()
            if result is not None:
                result['name'] = id

                pageload = models.GooglePageLoad(
                    id=id,
                    dt=datetime.datetime.now(),
                    auto=auto,
                    # Store the results as JSON, rather than on model fields.
                    result=json.dumps(result))
                pageload.put()

                results.append(result)

        return results

class LogHandler(webapp.RequestHandler):
    def get(self):

        context = {
            'tests': models.GooglePageLoad.all().order('-dt')[0:100]
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/log.html')
        self.response.out.write(template.render(path, context))

class ResultsHandler(webapp.RequestHandler):
    def get(self):

        unfulfilled_test_runs = models.WptTestRun.all().filter('results_received =', False)

        requests = {}
        results = []

        # Ping off a bunch of async requests.
        for test in unfulfilled_test_runs:
            requests[test.id] = WptTestResultsRequest(test.test_id)

        for id in requests:
            xml = requests[id].get_response()
            if xml is not None:

                if xml.getElementsByTagName('statusCode')[0].childNodes[0].data == '200':

                    testrun = unfulfilled_test_runs.filter('id =', id).fetch(1)[0]

                    wpt_result = models.WptTestResult(
                        id=id,
                        dt=datetime.datetime.now(),
                        auto=testrun.auto,
                        # Store the results as JSON, rather than on model fields.
                        result=xml.toxml())
                    wpt_result.put()

                    results.append(wpt_result)

                    # Mark the testrun as fulfilled
                    testrun.results_received = True
                    testrun.put()

        #path = os.path.join(os.path.dirname(__file__), 'templates/log.html')
        self.response.out.write("Worked" + str(dir(results)))


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/load', LoadHandler),
        ('/results', ResultsHandler),
        ('/log', LogHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()