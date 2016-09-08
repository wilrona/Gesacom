__author__ = 'Ronald'

from google.appengine.ext import ndb


class Societe(ndb.Model):
    name = ndb.StringProperty()
    bp = ndb.StringProperty()
    adress = ndb.StringProperty()
    ville = ndb.StringProperty()
    pays = ndb.StringProperty()
    phone = ndb.StringProperty()
    capital = ndb.StringProperty()
    numcontr = ndb.StringProperty()
    registcom = ndb.StringProperty()
    email = ndb.StringProperty()
    siteweb = ndb.StringProperty()
    slogan = ndb.StringProperty()
    typEnt = ndb.StringProperty()

    def make_to_dict(self):
        to_dict = {}

        to_dict['name'] = self.name
        to_dict['bp'] = self.bp
        to_dict['adress'] = self.adress
        to_dict['ville'] = self.ville
        to_dict['pays'] = self.pays
        to_dict['phone'] = self.phone
        to_dict['capital'] = self.capital
        to_dict['numcontr'] = self.numcontr
        to_dict['registcom'] = self.registcom
        to_dict['email'] = self.email
        to_dict['siteweb'] = self.siteweb
        to_dict['slogan'] = self.slogan
        to_dict['typEnt'] = self.typEnt

        return to_dict

