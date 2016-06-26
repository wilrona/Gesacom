__author__ = 'Ronald'

from google.appengine.ext import ndb



class fdt_coll(ndb.Model):
    absence = ndb.FloatProperty()
    conge = ndb.FloatProperty()
    ferier = ndb.FloatProperty()
    administration = ndb.FloatProperty()
    formation = ndb.FloatProperty()
    developpement = ndb.FloatProperty()
    prod_fact = ndb.FloatProperty()
    prod_nfact = ndb.FloatProperty()
    heure_nchargee = ndb.FloatProperty()


