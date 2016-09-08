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

    def make_to_dict(self):
        to_dict = {}

        to_dict['name'] = self.name
        to_dict['description'] = self.description
        to_dict['active'] = self.active

        profil_role = ProfilRole.query(
            ProfilRole.profil_id == self.key
        )

        roles = [{
            'role': role.role_id.get().valeur,
            'edit': role.edit,
            'delecte': role.delete
        } for role in profil_role]

        to_dict['roles'] = roles

        return to_dict



class ProfilRole(ndb.Model):
    role_id = ndb.KeyProperty(kind=Roles)
    profil_id = ndb.KeyProperty(kind=Profil)
    edit = ndb.BooleanProperty()
    delete = ndb.BooleanProperty()