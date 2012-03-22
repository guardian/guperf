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
from pagespeed import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest
from utils import OrderedDictYAMLLoader, xml_to_json
from wpt import WptResultData

class LoadHandler(webapp.RequestHandler):
    """
    - Load data for list of URLs.
    - For each URL create new test entry in db.
    - Just stash the JSON response to query for data later.
    """

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
                    score=result['score'],
                    # Store the results as JSON, rather than on model fields.
                    result=json.dumps(result))
                pageload.put()

                results.append(result)

        return results

class DashboardHandler(webapp.RequestHandler):
    """
    - Get latest data from db for each test URL, pass to template.
    """
    def get(self):

        urls = yaml.load(open('urls_to_test.yaml','r').read(), OrderedDictYAMLLoader)
        context = {
            'results': []
        }
        
        for id in urls:
            gq = models.GooglePageLoad.all()
            wptq = models.WptTestResult.all()
            g_result = gq.filter('id =', id).order('-dt').fetch(1)[0]
            wpt_result = wptq.filter('id =', id).order('-dt').fetch(1)[0]

            result = {
                'google': json.loads(g_result.result),
                'wpt': xml_to_json(wpt_result.result)
            }
            
            # Get the last 10 automated page scores to graph.
            history = gq.filter('id =', id).filter('auto =', True).order('-dt').fetch(10)
            score_history = [load.score for load in history]

            logging.debug(score_history)

            # Get the last 10 PLTs to graph.
            history = wptq.filter('id =', id).filter('auto =', True).order('-dt').fetch(10)
            plt_history = []
            for load in history:
                parsed = xml_to_json(load.result)
                plt_history.append({
                    'time': load.dt,
                    'plt1': parsed['data']['average']['firstView']['loadTime'],
                    'plt2': parsed['data']['average']['repeatView']['loadTime'],
                    'render1': parsed['data']['average']['firstView']['render'],
                    'render2': parsed['data']['average']['repeatView']['render'],
                    'score': score_history.pop(0)
                })
            plt_history.reverse()

            # Get the top five rules by impact.
            rules_by_impact = []
            for rule_result in result['google']['formattedResults']['ruleResults'].values():
                rules_by_impact.append({
                    'name': rule_result['localizedRuleName'],
                    'impact': rule_result['ruleImpact']
                })
            rules_by_impact = sorted(rules_by_impact, key=lambda k: k['impact'], reverse=True)

            # Put some other useful data into context.
            result['name'] = id
            result['url'] = result['google']['id']
            result['id'] = id.replace(' ', '-')
            result['rules_by_impact'] = rules_by_impact[0:7]
            result['google']['score_history'] = score_history
            result['wpt']['plt_history'] = plt_history

            context['results'].append(result)

        path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
        self.response.out.write(template.render(path, context))

class LogHandler(webapp.RequestHandler):
    def get(self):

        context = {
            'tests': models.PageLoad.all().order('-dt')[0:100]
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

                testrun = unfulfilled_test_runs.filter('id =', id).fetch(1)[0]

                if xml.getElementsByTagName('statusCode')[0].childNodes[0].data == '200':

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
        ('/', DashboardHandler),
        ('/load', LoadHandler),
        ('/results', ResultsHandler),
        ('/log', LogHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()