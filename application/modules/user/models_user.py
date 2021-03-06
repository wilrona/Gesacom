__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..role.models_role import Roles
from ..site.models_site import Site
from ..departement.models_dep import Departement
from ..fonction.models_fct import Fonction
from ..grade.models_grade import Grade


class Users(ndb.Model):

    email = ndb.StringProperty()
    date_create = ndb.DateTimeProperty()
    matricule = ndb.StringProperty()

    is_enabled = ndb.BooleanProperty(default=False)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    logged = ndb.BooleanProperty(default=False)
    date_last_logged = ndb.DateTimeProperty()
    google_id = ndb.StringProperty()
    date_update = ndb.DateTimeProperty()

    fonction_id = ndb.KeyProperty(kind=Fonction)
    site_id = ndb.KeyProperty(kind=Site)
    departement_id = ndb.KeyProperty(kind=Departement)
    grade_id = ndb.KeyProperty(kind=Grade)

    tauxH = ndb.FloatProperty(default=0.00)
    date_start = ndb.DateProperty()

    def is_active(self):
        return self.is_enabled

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = ''+str(self.last_name)+' '+str(self.first_name)+''
        return full_name

    def has_roles(self, requirements, accesibles=None):

        user_role = UserRole.query(
            UserRole.user_id == self.key
        )

        user_roles = [role.role_id.get().valeur for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True

                        if accesibles and role_name != 'super_admin':
                            role = Roles.query(
                                Roles.valeur == role_name
                            ).get()

                            role_user = UserRole.query(
                                UserRole.user_id == self.key,
                                UserRole.role_id == role.key
                            ).get()

                            for accesible in accesibles:
                                if accesible == 'edit' and not role_user.edit:
                                    authorized = False
                                    break
                                if accesible == 'delete' and not role_user.delete:
                                    authorized = False
                                    break
                        else:
                            break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
                else:
                    return True
            else:
                # this is a role_name requirement
                role_name = requirement

                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False
                else:
                    if accesibles and role_name != 'super_admin':

                        role = Roles.query(
                                Roles.valeur == role_name
                        ).get()

                        role_user = UserRole.query(
                            UserRole.user_id == self.key,
                            UserRole.role_id == role.key
                        ).get()

                        for accesible in accesibles:
                            if accesible == 'edit' and not role_user.edit:
                                return False
                            if accesible == 'delete' and not role_user.delete:
                                return False

        # All requirements have been met: return True
        return True

    def time_user(self, date_start=None, date_end=None):
        from ..temps.models_temps import DetailTemps, Temps

        the_time_user = []

        temps = Temps.query(Temps.user_id == self.key)

        for temp in temps:
            if date_start and date_end:
                details = DetailTemps.query(
                    DetailTemps.date >= date_start,
                    DetailTemps.date <= date_end,
                    DetailTemps.temps_id == temp.key
                )
            else:

                details = DetailTemps.query(
                    DetailTemps.temps_id == temp.key
                )
            for detail in details:
                the_time_user.append(detail)

        return the_time_user

    def projet_user(self):
        from ..tache.models_tache import Tache

        List_projet = []

        for tache in Tache.query(Tache.user_id == self.key):
            if tache.projet_id and tache.projet_id.get().facturable and tache.projet_id.get().key.id() not in List_projet:
                List_projet.append(tache.projet_id.get())

        return List_projet

    def valeur_facture(self):

        montant = 0.0
        for projet_id in self.projet_user():
            ratio = projet_id.ratio_user(self.key.id())

            montant_sur_projet = projet_id.montant * ratio

            montant += montant_sur_projet

        return montant

    def make_to_dict(self):

        to_dict = {}
        to_dict['email'] = self.email
        to_dict['date_create'] = str(self.date_create)
        to_dict['matricule'] = self.matricule
        to_dict['is_enabled'] = self.is_enabled
        to_dict['first_name'] = self.first_name
        to_dict['last_name'] = self.last_name
        to_dict['logged'] = self.logged
        to_dict['date_last_logged'] = str(self.date_last_logged)
        to_dict['google_id'] = self.google_id
        to_dict['date_update'] = str(self.date_update)
        to_dict['tauxH'] = self.tauxH
        to_dict['date_start'] = str(self.date_start)

        to_dict['fonction_id'] = None
        if self.fonction_id:
            to_dict['fonction_id'] = self.fonction_id.get().libelle

        to_dict['site_id'] = None
        if self.site_id:
            to_dict['site_id'] = self.site_id.get().libelle
        to_dict['departement_id'] = None
        if self.departement_id:
            to_dict['departement_id'] = self.departement_id.get().libelle
        to_dict['grade_id'] = None
        if self.grade_id:
            to_dict['grade_id'] = self.grade_id.get().libelle

        role = UserRole.query(
            UserRole.user_id == self.key
        )
        roles = [{
            'role': rol.role_id.get().valeur,
            'edit': rol.edit,
            'delete': rol.delete
        } for rol in role]

        to_dict['roles'] = roles


        horaire = Horaire.query(
            Horaire.user == self.key
        )
        horaires = [{
            'montant': horai.montant,
            'date_start': str(horai.date_start)
        } for horai in horaire]

        to_dict['horaires'] = horaires

        return to_dict


class UserRole(ndb.Model):
    user_id = ndb.KeyProperty(kind=Users)
    role_id = ndb.KeyProperty(kind=Roles)
    edit = ndb.BooleanProperty()
    delete = ndb.BooleanProperty()


class Horaire(ndb.Model):
    date_start = ndb.DateProperty()
    montant = ndb.FloatProperty()
    user = ndb.KeyProperty(kind=Users)






