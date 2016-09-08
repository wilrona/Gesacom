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

    def make_to_dict(self):
        to_dict = {}
        to_dict['code'] = self.code
        to_dict['libelle'] = self.libelle

        serv = Service.query(
            Service.domaine == self.key
        )

        services = [{
            'code': service.code,
            'libelle': service.libelle
        } for service in serv]

        to_dict['services'] = services

        return to_dict


class Service(ndb.Model):
    code = ndb.StringProperty()
    libelle = ndb.StringProperty()
    domaine = ndb.KeyProperty(kind=Domaine)