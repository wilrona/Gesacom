__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..role.models_role import Roles


class Profil(ndb.Model):
    name = ndb.StringProperty()
    description = ndb.TextProperty()
    active = ndb.BooleanProperty(default=True)

    def count_role(self):
        profil_role_exist = ProfilRole.query(
            ProfilRole.profil_id == self.key
        ).count()

        return profil_role_exist


class ProfilRole(ndb.Model):
    role_id = ndb.KeyProperty(kind=Roles)
    profil_id = ndb.KeyProperty(kind=Profil)
    edit = ndb.BooleanProperty()
    delete = ndb.BooleanProperty()