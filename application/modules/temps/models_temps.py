__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..user.models_user import Users
from ..tache.models_tache import Tache
from ..frais.models_frais import FraisProjet


class Temps(ndb.Model):
    date_start = ndb.DateProperty()
    date_end = ndb.DateProperty()
    user_id = ndb.KeyProperty(kind=Users)
    tache_id = ndb.KeyProperty(kind=Tache)

    def make_to_dict(self):

        to_dict = {}

        to_dict['user_id'] = self.user_id.get().email

        detail = DetailTemps.query(
            DetailTemps.temps_id == self.key
        )

        details = [{
            'date': str(dels.date),
            'description': dels.description,
            'heure': str(dels.heure),
            'jour': dels.jour,
            'conversion': dels.conversion,
            'ordre': dels.ordre,
            'parent': dels.parent
        } for dels in detail]

        to_dict['details'] = details

        return to_dict


class DetailTemps(ndb.Model):
    date = ndb.DateProperty()
    description = ndb.TextProperty()
    heure = ndb.TimeProperty()
    jour = ndb.IntegerProperty()
    conversion = ndb.FloatProperty()
    temps_id = ndb.KeyProperty(kind=Temps)
    ordre = ndb.IntegerProperty()
    parent = ndb.IntegerProperty()


class DetailFrais(ndb.Model):
    date = ndb.DateProperty()
    description = ndb.TextProperty()
    montant = ndb.FloatProperty()
    detail_fdt = ndb.KeyProperty(kind=DetailTemps)
    temps_id = ndb.KeyProperty(kind=Temps)
    frais_projet_id = ndb.KeyProperty(kind=FraisProjet)
