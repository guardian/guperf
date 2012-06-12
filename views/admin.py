
import logging
import os
import httplib
import datetime
from urlparse import urlparse

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api.datastore_errors import BadValueError

import models
from utils import check_http_200, get_messages, add_message

class StatusHandler(webapp.RequestHandler):

    def get(self):
        
        context = {
            'total_urls': models.Url.all().count(),
            'jobs_in_queue': models.UrlTestTask.all().count(),
            'tests_awaiting_results': models.TestResult.all().filter('results_received =', False).count(),
            'total_tests': models.TestResult.all().count(),
            'dashboards': models.Dashboard.all(),
        }

        self.response.out.write(template.render('templates/admin/status.html', context))



class AdminHandler(webapp.RequestHandler):

    def get(self):

        context = {
            'urls': models.Url.all(),
            'dashboards': models.Dashboard.all(),
            'error': self.request.get('e'),
            'messages': get_messages()
        }

        self.response.out.write(template.render('templates/admin/urls.html', context))

    def post(self):

        if self.request.get('method') == 'delete':
            self.delete()

        else:

            context = {
                'urls': models.Url.all(),
                'dashboards': models.Dashboard.all(),
                'adding': self.request.get('model'),
                'fields': {
                    'name': self.request.get('name'),
                    'url': self.request.get('url'),
                    'dashboard': self.request.get('dashboard'),
                    'dashboardname': self.request.get('dashboard-name'),
                    'dashboardid': self.request.get('dashboard-id')
                }
            }

            if context['adding'] == 'url':

                link = 'http://' + self.request.get('url').replace('http://', '')

                if check_http_200(link):
                    try:
                        url = models.Url(
                            name=self.request.get('name'),
                            url=link,
                            dashboard=self.request.get('dashboard'))
                        url.put()
                        add_message('URL added successfully.')
                        return self.redirect('/admin/urls')
                    except BadValueError:
                        context['error'] = "BadValueError"
                else:
                    context['error'] = '200'

            elif context['adding'] == 'dashboard':
                try:
                    dashboard = models.Dashboard(
                                name=self.request.get('dashboard-name'),
                                id=self.request.get('dashboard-id'))
                    dashboard.put()
                    add_message('Dashboard added successfully. Now add some test URLs.')
                    return self.redirect('/admin/urls')


                except BadValueError:
                    context['error'] = "BadValueError"

            context['messages'] = get_messages()
            logging.debug(context['messages'])
    
            self.response.out.write(template.render('templates/admin/urls.html', context))


    def delete(self):
        url = models.Url.get(self.request.get('key'))
        url.delete()
        add_message('URL deleted successfully.')

        return self.redirect('/admin/urls')
