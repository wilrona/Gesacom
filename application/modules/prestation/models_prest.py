__author__ = 'Ronald'

from google.appengine.ext import ndb

class Prestation(ndb.Model):
    libelle = ndb.StringProperty()
    factu = ndb.BooleanProperty()
    nfactu = ndb.BooleanProperty()
    sigle = ndb.StringProperty()

    def make_to_dict(self):

        to_dict = {}
        to_dict['libelle'] = self.libelle
        to_dict['factu'] = self.factu
        to_dict['nfactu'] = self.nfactu
        to_dict['sigle'] = self.sigle

        return to_dict