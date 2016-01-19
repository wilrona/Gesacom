__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..user.models_user import Users
from ..prestation.models_prest import Prestation
from ..charge.models_charge import Charge
from ..client.models_client import Client


class Budget(ndb.Model):
    heure = ndb.IntegerProperty()
    user_id = ndb.KeyProperty(kind=Users)
    date_start = ndb.DateProperty()


class BudgetPrestation(ndb.Model):
    prestation_id = ndb.KeyProperty(kind=Prestation)
    budget_id = ndb.KeyProperty(kind=Budget)
    heure = ndb.IntegerProperty()


class ChargeBudget(ndb.Model):
    charge_id = ndb.KeyProperty(kind=Charge)
    montant = ndb.FloatProperty()
    date_app = ndb.DateProperty()


class ClientBudget(ndb.Model):
    date_app = ndb.DateProperty()
    montant = ndb.FloatProperty()
    client_id = ndb.KeyProperty(kind=Client)