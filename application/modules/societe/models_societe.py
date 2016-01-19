__author__ = 'Ronald'

from google.appengine.ext import ndb


class Societe(ndb.Model):
    name = ndb.StringProperty()
    bp = ndb.StringProperty()
    adress = ndb.StringProperty()
    ville = ndb.StringProperty()
    pays = ndb.StringProperty()
    phone = ndb.StringProperty()
    capital = ndb.StringProperty()
    numcontr = ndb.StringProperty()
    registcom = ndb.StringProperty()
    email = ndb.StringProperty()
    siteweb = ndb.StringProperty()
    slogan = ndb.StringProperty()
    typEnt = ndb.StringProperty()

