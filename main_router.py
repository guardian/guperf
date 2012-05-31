#!/usr/bin/env python

import logging

from views.load import LoadHandler, CompetitorLoadHandler, ResultsHandler, LogHandler
from views.dashboard import DashboardHandler, BetaDashboardHandler
from views.competitors import CompetitorsHandler
from views.management import StatusHandler, BetaStatusHandler

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
        ('/management/status', StatusHandler),
        ('/beta/management/status', BetaStatusHandler),
        ('/beta', BetaDashboardHandler),
        ('/', DashboardHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()