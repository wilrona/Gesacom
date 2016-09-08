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
    montant_projet_fdt = ndb.FloatProperty()

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
                time = tache.detail_heure

                pre_total = user_taux * time

                total += pre_total
        ratio = 0.0
        if self.montant_projet_fdt:
            ratio = total / self.montant_projet_fdt

        return round(ratio, 1)

    def make_to_dict(self):

        to_dict = {}

        to_dict['code'] = self.code
        to_dict['titre'] = self.titre
        to_dict['heure'] = self.heure
        to_dict['montant'] = self.montant
        to_dict['date_start'] = str(self.date_start)
        to_dict['date_end'] = str(self.date_end)
        to_dict['facturable'] = self.facturable
        to_dict['domaine_id'] = self.domaine_id.get().libelle
        to_dict['client_id'] = self.client_id.get().ref
        to_dict['service_id'] = self.service_id.get().code
        to_dict['prospect_id'] = None
        if self.prospect_id:
            to_dict['prospect_id'] = self.prospect_id.get().ref
        to_dict['responsable_id'] = self.responsable_id.get().matricule
        to_dict['closed'] = self.closed
        to_dict['suspend'] = self.suspend
        to_dict['montant_projet_fdt'] = self.montant_projet_fdt

        from ..frais.models_frais import FraisProjet

        fraisis = FraisProjet.query(
            FraisProjet.projet_id == self.key
        )

        Frais = [{
            'montant': fraise.montant,
            'facturable': fraise.facturable,
            'frais_id': fraise.frais_id.get().libelle
        } for fraise in fraisis]

        to_dict['frais'] = Frais

        return to_dict