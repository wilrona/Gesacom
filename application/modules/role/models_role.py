__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class roles(polymodel.PolyModel):
    titre = ndb.StringProperty()
    description = ndb.TextProperty()
    valeur = ndb.StringProperty()
    action = ndb.IntegerProperty()
    active = ndb.BooleanProperty(default=True)


class Roles(roles):
    parent = ndb.KeyProperty(kind=roles)