__author__ = 'Ronald'

from google.appengine.ext import ndb


class Domaine(ndb.Model):
    code = ndb.StringProperty()
    libelle = ndb.StringProperty()

    def count_service(self):
        ser = Service.query(
            Service.domaine == self.key
        ).count()

        return ser


class Service(ndb.Model):
    code = ndb.StringProperty()
    libelle = ndb.StringProperty()
    domaine = ndb.KeyProperty(kind=Domaine)