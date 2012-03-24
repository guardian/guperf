#!/usr/bin/env python

import logging

from views.load import LoadHandler, ResultsHandler, LogHandler
from views.dashboard import DashboardHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/load', LoadHandler),
        ('/results', ResultsHandler),
        ('/log', LogHandler),
        ('/', DashboardHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()