__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..user.models_user import Users
from ..prestation.models_prest import Prestation
from ..charge.models_charge import Charge
from ..client.models_client import Client


class Budget(ndb.Model):
    heure = ndb.FloatProperty()
    user_id = ndb.KeyProperty(kind=Users)
    date_start = ndb.DateProperty()

    def make_to_dict(self):

        to_dict = {}
        to_dict['heure'] = self.heure
        to_dict['date_start'] = str(self.date_start)
        to_dict['user_id'] = self.user_id.get().email

        bud_pres = BudgetPrestation.query(
            BudgetPrestation.budget_id == self.key
        )

        budg_pres = [{
            'heure': bud.heure,
            'prestation_id': bud.prestation_id.get().sigle
        } for bud in bud_pres]

        to_dict['budget_prestation'] = budg_pres

        return to_dict


class BudgetPrestation(ndb.Model):
    prestation_id = ndb.KeyProperty(kind=Prestation)
    budget_id = ndb.KeyProperty(kind=Budget)
    heure = ndb.FloatProperty()


class ChargeBudget(ndb.Model):
    charge_id = ndb.KeyProperty(kind=Charge)
    montant = ndb.FloatProperty()
    date_app = ndb.DateProperty()


class ClientBudget(ndb.Model):
    date_app = ndb.DateProperty()
    montant = ndb.FloatProperty()
    client_id = ndb.KeyProperty(kind=Client)