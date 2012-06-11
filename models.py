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

class Url(db.Expando):
	name = db.StringProperty(required=True)
	url = db.LinkProperty(required=True)
	dashboard = db.StringProperty(required=True)

class UrlTestTask(db.Expando):
	name = db.StringProperty()
	url = db.StringProperty()
	dt = db.DateTimeProperty()
