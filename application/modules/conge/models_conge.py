__author__ = 'Ronald'

from google.appengine.ext import ndb


class Ferier(ndb.Model):
    date = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    apply = ndb.BooleanProperty(default=False)