#!/usr/bin/env python

import logging

from views.load import LoadHandler, CompetitorLoadHandler, ResultsHandler, LogHandler
from views.dashboard import DashboardHandler
from views.competitors import CompetitorsHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/load', LoadHandler),
        ('/colleagues-load', CompetitorLoadHandler),
        ('/results', ResultsHandler),
        ('/log', LogHandler),
        ('/colleagues', CompetitorsHandler),
        ('/', DashboardHandler)
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()