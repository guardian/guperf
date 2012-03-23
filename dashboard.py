
import logging
import os
import yaml

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

import models
from utils import xml_to_json, get_urls

class DashboardHandler(webapp.RequestHandler):

    def get_test_results(self, provider, url):
    	return models.TestResult.all().filter('url =', url).filter('provider =', provider).filter('results_received', True).order('-dt')

    def get(self):

        urls = get_urls()
        context = {
            'results': []
        }
        
        for url in urls:
            try:
            	g_results = self.get_test_results('google', url)
            	wpt_results = self.get_test_results('wpt', url)
            except:
                self.response.out.write("Some test urls don't have even one result yet, so let's just bail out. Early days.")
                return

            result = {
                'google': json.loads(g_results.fetch(1)[0].result),
                'wpt': xml_to_json(wpt_results.fetch(1)[0].result)
            }
            
            # Get the last 10 automated page scores to graph.
            score_history = [json.loads(load.result)['score'] for load in g_results.filter('auto =', True).fetch(10)]

            # Get the last 10 automated PLTs to graph.
            history = wpt_results.filter('auto =', True).fetch(10)
            plt_history = []
            for load in history:
                parsed = xml_to_json(load.result)
                plt_history.append({
                    'time': load.dt,
                    'plt1': parsed['data']['median']['firstView']['loadTime'],
                    'plt2': parsed['data']['median']['repeatView']['loadTime'],
                    'render1': parsed['data']['median']['firstView']['render'],
                    'render2': parsed['data']['median']['repeatView']['render'],
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
            result['name'] = url
            result['url'] = result['google']['id']
            result['id'] = url.replace(' ', '-')
            result['rules_by_impact'] = rules_by_impact[0:7]
            result['google']['score_history'] = score_history
            result['wpt']['plt_history'] = plt_history

            context['results'].append(result)

        path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
        self.response.out.write(template.render(path, context))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/', DashboardHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()