__author__ = 'Ronald'

from google.appengine.ext import ndb

class Prestation(ndb.Model):
    libelle = ndb.StringProperty()
    factu = ndb.BooleanProperty()
    nfactu = ndb.BooleanProperty()
    sigle = ndb.StringProperty()