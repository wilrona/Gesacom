__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..domaine.models_domaine import Domaine, Service
from ..client.models_client import Client
from ..user.models_user import Users


class Projet(ndb.Model):
    code = ndb.StringProperty()
    titre = ndb.StringProperty()
    heure = ndb.IntegerProperty()
    montant = ndb.FloatProperty()
    date_start = ndb.DateProperty()
    date_end = ndb.DateProperty()
    facturable = ndb.BooleanProperty()
    domaine_id = ndb.KeyProperty(kind=Domaine)
    client_id = ndb.KeyProperty(kind=Client)
    service_id = ndb.KeyProperty(kind=Service)
    prospect_id = ndb.KeyProperty(kind=Client)
    responsable_id = ndb.KeyProperty(kind=Users)
    closed = ndb.BooleanProperty(default=False)
    suspend = ndb.BooleanProperty(default=False)

    def montant_projet_fdt(self):
        from ..tache.models_tache import Tache

        tache_projet = Tache.query(
            Tache.projet_id == self.key
        )

        total = 0.0
        for tache in tache_projet:
            if tache.prestation_sigle() == 'PRO' and tache.facturable:
                user_taux = tache.user_id.get().tauxH
                time = 0.0
                for times in tache.time_tache():
                    time += times.conversion

                pre_total = user_taux * time

                total += pre_total

        return total

    def ratio_user(self, user_id):
        from ..tache.models_tache import Tache, Users

        user = Users.get_by_id(int(user_id))

        tache_projet = Tache.query(
            Tache.projet_id == self.key,
            Tache.user_id == user.key
        )

        total = 0.0
        for tache in tache_projet:
            if tache.prestation_sigle() == 'PRO' and tache.facturable:
                user_taux = tache.user_id.get().tauxH
                time = 0.0
                for times in tache.time_tache():
                    time += times.conversion

                pre_total = user_taux * time

                total += pre_total

        ratio = 0.0

        if total:
            ratio = total / self.montant_projet_fdt()

        return round(ratio, 1)