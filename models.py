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

	def display_url(self):
		return self.url[:100]

class UrlTestTask(db.Expando):
	name = db.StringProperty()
	url = db.StringProperty()
	dt = db.DateTimeProperty()

class Dashboard(db.Expando):
	name = db.StringProperty(required=True)
	id = db.StringProperty(required=True)

class UserMessage(db.Expando):
	body = db.TextProperty()
	dt = db.DateTimeProperty()
