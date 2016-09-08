__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..projet.models_projet import Projet, Users
from ..prestation.models_prest import Prestation


class Tache(ndb.Model):
    titre = ndb.StringProperty()
    description = ndb.TextProperty()
    heure = ndb.IntegerProperty()
    date_start = ndb.DateProperty()
    facturable = ndb.BooleanProperty()
    projet_id = ndb.KeyProperty(kind=Projet)
    user_id = ndb.KeyProperty(kind=Users)
    prestation_id = ndb.KeyProperty(kind=Prestation)
    end = ndb.BooleanProperty(default=False)
    closed = ndb.BooleanProperty(default=False)
    detail_heure = ndb.FloatProperty()

    def prestation_sigle(self):
        return self.prestation_id.get().sigle

    def make_to_dict(self):

        to_dict = {}
        to_dict['titre'] = self.titre
        to_dict['description'] = self.description
        to_dict['heure'] = self.heure
        to_dict['date_start'] = str(self.date_start)
        to_dict['facturable'] = self.facturable
        to_dict['projet_id'] = None
        if self.projet_id:
            to_dict['projet_id'] = self.projet_id.get().code
        to_dict['user_id'] = None
        if self.user_id:
            to_dict['user_id'] = self.user_id.get().email
        to_dict['prestation_id'] = None
        if self.prestation_id:
            to_dict['prestation_id'] = self.prestation_id.get().sigle
        to_dict['end'] = self.end
        to_dict['closed'] = self.closed
        to_dict['detail_heure'] = self.detail_heure

        from ..temps.models_temps import Temps

        temps = Temps.query(
            Temps.tache_id == self.key
        )

        Temps = [{
            'date_start':  str(tem.date_start),
            'date_end': str(tem.date_end),
            'list_temps': tem.make_to_dict()
        } for tem in temps]

        to_dict['temps'] = Temps

        return to_dict

    # def time_tache(self):
    #     from ..temps.models_temps import Temps, DetailTemps
    #
    #     time_taches = []
    #
    #     for temps in Temps.query(Temps.tache_id == self.key):
    #         details = DetailTemps.query(
    #             DetailTemps.temps_id == temps.key
    #         )
    #         for detail in details:
    #             time_taches.append(detail)
    #
    #     return time_taches

