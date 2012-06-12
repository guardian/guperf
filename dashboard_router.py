#!/usr/bin/env python

import logging

from views.dashboard import DashboardHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/dashboard/(.*)', DashboardHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()