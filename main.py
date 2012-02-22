#!/usr/bin/env python

import logging
import os
import yaml
import datetime
import json

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

import models
from pagespeed import PageSpeedRequest

class LoadHandler(webapp.RequestHandler):
    """
    - Load data for list of URLs.
    - For each URL create new test entry in db.
    - Pull out data we are specifically interested in, but stash entire JSON response as well.
    - Add load_type field. Was this a daily load query, or a manual request.
    """
    def get(self):
        urls = yaml.load(open('urls_to_test.yaml','r').read())

        auto = self.request.get("auto", False)
        if auto is not False:
            auto = True

        logging.debug(auto)

        requests = {}
        context = {}

        # Ping off a bunch of async requests.
        for id in urls:
            requests[id] = PageSpeedRequest(urls[id])

        for id in requests:
            result = requests[id].get_result()

            pageload = models.PageLoad(
                id=id,
                dt=datetime.datetime.now(),
                auto=auto,
                result=json.dumps(result))
            pageload.put()

            context[id] = result

        path = os.path.join(os.path.dirname(__file__), 'templates/loaded.html')
        self.response.out.write(template.render(path, context))


class DashboardHandler(webapp.RequestHandler):
    """
    - Get latest data from db for each test URL, pass to template.
    """
    def get(self):

        urls = yaml.load(open('urls_to_test.yaml','r').read())
        logging.debug(urls)
        context = {}
        
        for id in urls:
            q = models.PageLoad.all()
            p = q.filter('id =', id).order('dt').fetch(1)[0]
            context[id] = json.loads(p.result)

        logging.debug(context)

        path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
        self.response.out.write(template.render(path, context))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/', DashboardHandler), ('/load', LoadHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()