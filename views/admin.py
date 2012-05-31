
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

        urls = models.Url.all()

        self.response.out.write(template.render('templates/admin.html', {'urls': urls, 'error': self.request.get('e')}))

    def post(self):

        if self.request.get('method') == 'delete':
            self.delete()

        else:

            urls = models.Url.all()

            link = 'http://' + self.request.get('url').replace('http://', '')

            if check_http_200(link):
                    logging.debug(self.request.get('dashboard'))
                    logging.debug(self.request.get('name'))
                    logging.debug(link)
                    url = models.Url(
                        name=self.request.get('name'),
                        url=link,
                        dashboard=self.request.get('dashboard'))
                    url.put()

                    self.redirect('/admin/urls')



            else:
                self.response.out.write(template.render('templates/admin.html', {'urls': urls, 'error': '200'}))


    def delete(self):
        url = models.Url.get(self.request.get('key'))
        url.delete()

        self.redirect('/admin/urls')
