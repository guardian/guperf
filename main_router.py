#!/usr/bin/env python

import logging

from views.load import ScheduleHandler, JobHandler, ResultsHandler, LogHandler
from views.dashboard import DashboardHandler, BetaDashboardHandler
from views.management import StatusHandler, BetaStatusHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/schedule', ScheduleHandler),
        ('/dojob', JobHandler),
        ('/results', ResultsHandler),
        ('/log', LogHandler),
        ('/management/status', StatusHandler),
        ('/beta/management/status', BetaStatusHandler),
        ('/beta', BetaDashboardHandler),
        ('/', DashboardHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()