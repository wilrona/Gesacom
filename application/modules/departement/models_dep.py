__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..societe.models_societe import Societe

class Departement(ndb.Model):
    libelle = ndb.StringProperty()
    societe = ndb.KeyProperty(kind=Societe)

    def count_user(self):
        from ..user.models_user import Users

        user_exist = Users.query(
            Users.departement == self.key
        ).count()

        return user_exist

    def make_to_dict(self):
        to_dict = {}

        to_dict['libelle'] = self.libelle

        return to_dict