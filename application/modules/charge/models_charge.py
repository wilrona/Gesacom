__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..societe.models_societe import Societe

class Charge(ndb.Model):
    libelle = ndb.StringProperty()
    societe = ndb.KeyProperty(kind=Societe)

    def count_budget(self):
        from ..budget.models_budget import ChargeBudget

        bugdet = ChargeBudget.query(
            ChargeBudget.charge_id == self.key
        ).count()

        return bugdet

    def make_to_dict(self):

        to_dict = {}
        to_dict['libelle'] = self.libelle

        from ..budget.models_budget import ChargeBudget

        bugdet_charge = ChargeBudget.query(
            ChargeBudget.charge_id == self.key
        )

        budget = [{
            'montant': bud.montant,
            'date_app': str(bud.date_app)
        } for bud in bugdet_charge]
        to_dict['budget'] = budget

        return to_dict

