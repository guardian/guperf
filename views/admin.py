
import logging
import os
import httplib
from urlparse import urlparse

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api.datastore_errors import BadValueError

import models
from utils import check_http_200

class AdminHandler(webapp.RequestHandler):

    def get(self):

        context = {
            'urls': models.Url.all(),
            'dashboards': models.Dashboard.all(),
            'error': self.request.get('e')
        }

        self.response.out.write(template.render('templates/admin.html', context))

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
                        self.redirect('/admin/urls')
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
                    self.redirect('/admin/urls')
                except BadValueError:
                    context['error'] = "BadValueError"
            
            self.response.out.write(template.render('templates/admin.html', context))


    def delete(self):
        url = models.Url.get(self.request.get('key'))
        url.delete()

        self.redirect('/admin/urls')
