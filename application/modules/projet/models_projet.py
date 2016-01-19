__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..domaine.models_domaine import Domaine, Service
from ..client.models_client import Client
from ..user.models_user import Users


class Projet(ndb.Model):
    code = ndb.StringProperty()
    titre = ndb.StringProperty()
    heure = ndb.IntegerProperty()
    montant = ndb.FloatProperty()
    date_start = ndb.DateProperty()
    date_end = ndb.DateProperty()
    facturable = ndb.BooleanProperty()
    domaine_id = ndb.KeyProperty(kind=Domaine)
    client_id = ndb.KeyProperty(kind=Client)
    service_id = ndb.KeyProperty(kind=Service)
    prospect_id = ndb.KeyProperty(kind=Client)
    responsable_id = ndb.KeyProperty(kind=Users)
    closed = ndb.BooleanProperty(default=False)
    suspend = ndb.BooleanProperty(default=False)