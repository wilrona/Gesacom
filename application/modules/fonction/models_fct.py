__author__ = 'Ronald'

from google.appengine.ext import ndb

class Fonction(ndb.Model):
    libelle = ndb.StringProperty()

    def count_user(self):
        from ..user.models_user import Users

        user_exist = Users.query(
            Users.fonction == self.key
        ).count()

        return user_exist

    def make_to_dict(self):

        to_dict = {}
        to_dict['libelle'] = self.libelle

        return to_dict