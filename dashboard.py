
import logging
import os
import yaml

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

import models
from utils import OrderedDictYAMLLoader, xml_to_json

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
            try:
                g_result = gq.filter('id =', id).order('-dt').fetch(1)[0]
                wpt_result = wptq.filter('id =', id).order('-dt').fetch(1)[0]
            except:
                self.response.out.write("Some test urls don't have any results yet, so let's just bail out.")
                return

            result = {
                'google': json.loads(g_result.result),
                'wpt': xml_to_json(wpt_result.result)
            }
            
            # Get the last 10 automated page scores to graph.
            history = gq.filter('id =', id).filter('auto =', True).order('-dt').fetch(10)
            score_history = [json.loads(load.result)['score'] for load in history]

            # Get the last 10 automated PLTs to graph.
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

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/', DashboardHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()