import logging

from google.appengine.ext import db

class GooglePageLoad(db.Expando):
	id = db.StringProperty()
	dt = db.DateTimeProperty()
	auto = db.BooleanProperty()
	result = db.TextProperty()

class WptTestRun(db.Expando):
	id = db.StringProperty()
	test_id = db.StringProperty()
	results_received = db.BooleanProperty()
	dt = db.DateTimeProperty()
	auto = db.BooleanProperty()
	result = db.TextProperty()

class WptTestResult(db.Expando):
	id = db.StringProperty()
	test_id = db.StringProperty()
	dt = db.DateTimeProperty()
	auto = db.BooleanProperty()
	result = db.TextProperty()