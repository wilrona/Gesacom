__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..projet.models_projet import Projet

class Frais(ndb.Model):
    libelle = ndb.StringProperty()
    factu = ndb.BooleanProperty()
    nfactu = ndb.BooleanProperty()

    def make_to_dict(self):

        to_dict = {}
        to_dict['libelle'] = self.libelle
        to_dict['factu'] = self.factu
        to_dict['nfactu'] = self.nfactu

        return to_dict



class FraisProjet(ndb.Model):
    montant = ndb.FloatProperty()
    facturable = ndb.BooleanProperty()
    projet_id = ndb.KeyProperty(kind=Projet)
    frais_id = ndb.KeyProperty(kind=Frais)