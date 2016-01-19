__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..projet.models_projet import Projet

class Frais(ndb.Model):
    libelle = ndb.StringProperty()
    factu = ndb.BooleanProperty()
    nfactu = ndb.BooleanProperty()



class FraisProjet(ndb.Model):
    montant = ndb.FloatProperty()
    facturable = ndb.BooleanProperty()
    projet_id = ndb.KeyProperty(kind=Projet)
    frais_id = ndb.KeyProperty(kind=Frais)