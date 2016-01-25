__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..user.models_user import Users
from ..tache.models_tache import Tache
from ..frais.models_frais import FraisProjet


class Temps(ndb.Model):
    date_start = ndb.DateProperty()
    date_end = ndb.DateProperty()
    user_id = ndb.KeyProperty(kind=Users)
    tache_id = ndb.KeyProperty(kind=Tache)


class DetailTemps(ndb.Model):
    date = ndb.DateProperty()
    description = ndb.TextProperty()
    heure = ndb.TimeProperty()
    conversion = ndb.FloatProperty()
    temps_id = ndb.KeyProperty(kind=Temps)
    ordre = ndb.IntegerProperty()


class DetailFrais(ndb.Model):
    date = ndb.DateProperty()
    description = ndb.TextProperty()
    montant = ndb.FloatProperty()
    detail_fdt = ndb.KeyProperty(kind=DetailTemps)
    temps_id = ndb.KeyProperty(kind=Temps)
    frais_projet_id = ndb.KeyProperty(kind=FraisProjet)
