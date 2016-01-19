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

