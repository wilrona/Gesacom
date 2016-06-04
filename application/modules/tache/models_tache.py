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

    def prestation_sigle(self):
        return self.prestation_id.get().sigle

    def time_tache(self):
        from ..temps.models_temps import Temps, DetailTemps

        time_taches = []

        for temps in Temps.query(Temps.tache_id == self.key):
            details = DetailTemps.query(
                DetailTemps.temps_id == temps.key
            )
            for detail in details:
                time_taches.append(detail)

        return time_taches

