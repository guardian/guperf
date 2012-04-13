from datetime import date, timedelta
import logging

from django.utils import simplejson as json

import models
from utils import xml_to_json

class NoDataError(Exception):
    pass

class ResultData(object):

    def __init__(self, url, provider, count):

        # Query for last 10 days of results.
        q = models.TestResult.all()
        q.filter('url =', url).filter('provider =', provider).filter('results_received', True)
        q.filter('dt >', date.today() - timedelta(days=10))
        q.order('dt')
        self.tests = q.fetch(count)

        if len(self.tests) < 1:
            raise NoDataError

        self.name = url
        self.id = url.replace(' ', '-')
        self.provider = provider

        self.tests = self.parse_raw_result_data()
        self.history = self.get_test_history(self.tests)
        self.current = self.tests[-1]
    
    def parse_raw_result_data(self, results):
        return results

    def get_test_history(self, tests):
        """
        Dedupe results based on date.
        """
        history = []
        for test in tests:
            if history == [] or test.dt.date() != history[-1].dt.date():
                history.append(test)
        return history

class GoogleResultData(ResultData):

    def __init__(self, url, count=10):
        super(GoogleResultData, self).__init__(url, 'google', count)
        self.rules_by_impact = self.get_rules_by_impact()
        self.url = self.current.result['id']

    def parse_raw_result_data(self):
        parsed = []
        for test in self.tests:
            test._result = json.loads(test.result)
            parsed.append(test)
        return parsed

    def get_rules_by_impact(self):
        rules_by_impact = []
        for rule_result in self.current.result['formattedResults']['ruleResults'].values():
            rules_by_impact.append({
                'name': rule_result['localizedRuleName'],
                'impact': rule_result['ruleImpact']
            })
        return sorted(rules_by_impact, key=lambda k: k['impact'], reverse=True)[0:7]

class WptResultData(ResultData):

    def __init__(self, url, count=10):
        super(WptResultData, self).__init__(url, 'wpt', count)

    def parse_raw_result_data(self):
        parsed = []
        for test in self.tests:
            test._result = xml_to_json(test.result)
            parsed.append(test)
        return parsed