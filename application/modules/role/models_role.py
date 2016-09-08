__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class roles(polymodel.PolyModel):
    titre = ndb.StringProperty()
    description = ndb.TextProperty()
    valeur = ndb.StringProperty()
    action = ndb.IntegerProperty()
    active = ndb.BooleanProperty(default=True)


class Roles(roles):
    parent = ndb.KeyProperty(kind=roles)

    def make_to_dict(self):
        to_dict = {}

        to_dict['titre'] = self.titre
        to_dict['description'] = self.description
        to_dict['valeur'] = self.valeur
        to_dict['action'] = self.action
        to_dict['active'] = self.active
        to_dict['parent'] = None
        if self.parent:
            to_dict['parent'] = self.parent.get().valeur

        return to_dict