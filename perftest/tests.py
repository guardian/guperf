import logging
import datetime

from django.utils import simplejson as json

import models
from requests import GooglePerfRequest, WptTestRunRequest, WptTestResultsRequest

def do_wpt_tests(urls, auto=False):

    requests = {}
    results = []

    # Ping off a bunch of async requests.
    for url in urls:
        logging.info("Making wpt testrun request for %s" % url)
        requests[url] = WptTestRunRequest(urls[url])

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

def get_wpt_results():

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
                logging.debug('we got a good result for %s' % url)
                unfulfilled_test_runs = models.TestResult.all().filter('results_received =', False).filter('provider =' ,'wpt')
                testrun = unfulfilled_test_runs.filter('url =', url).fetch(1)[0]
                testrun.result = xml.toxml()
                testrun.results_received = True
                testrun.put()
                results.append(testrun)
        else:
            logging.info("We tried to get results for %s, but no go." % url)

    return results


def do_google_tests(urls, auto=False):

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
