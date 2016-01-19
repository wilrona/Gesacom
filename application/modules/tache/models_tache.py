__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..projet.models_projet import Projet, Users
from ..prestation.models_prest import Prestation


class Tache(ndb.Model):
    titre = ndb.StringProperty()
    description = ndb.TextProperty()
    heure = ndb.IntegerProperty()
    date_start = ndb.DateProperty()
    facturable = ndb.BooleanProperty()
    projet_id = ndb.KeyProperty(kind=Projet)
    user_id = ndb.KeyProperty(kind=Users)
    prestation_id = ndb.KeyProperty(kind=Prestation)
    end = ndb.BooleanProperty(default=False)
    closed = ndb.BooleanProperty(default=False)
