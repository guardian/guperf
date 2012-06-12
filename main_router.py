#!/usr/bin/env python

import logging

from views.load import ScheduleHandler, JobHandler, ResultsHandler
from views.dashboard import DashboardHandler
from views.management import StatusHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

def main():

    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/schedule/(.*)', ScheduleHandler),
        ('/schedule', ScheduleHandler),
        ('/dojob', JobHandler),
        ('/results', ResultsHandler),
        ('/management/status', StatusHandler),
        ('/dashboard', DashboardHandler),
        ('/', DashboardHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()