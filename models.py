import logging

from google.appengine.ext import db

class TestResult(db.Expando):
	url = db.StringProperty()
	provider = db.StringProperty()
	dt = db.DateTimeProperty()
	auto = db.BooleanProperty()
	result = db.TextProperty()

	# If we have to poll for test results
	results_received = db.BooleanProperty()
	provider_id = db.StringProperty()