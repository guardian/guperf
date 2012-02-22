from google.appengine.ext import db


class PageLoad(db.Expando):
	id = db.StringProperty()
	dt = db.DateTimeProperty()
	auto = db.BooleanProperty()
	result = db.TextProperty()



