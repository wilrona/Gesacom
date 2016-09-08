__author__ = 'Ronald'

from google.appengine.ext import ndb


class Client(ndb.Model):
    name = ndb.StringProperty()
    ref = ndb.StringProperty()
    bp = ndb.StringProperty()
    adresse = ndb.TextProperty()
    ville = ndb.StringProperty()
    pays = ndb.StringProperty()
    email = ndb.StringProperty()
    phone = ndb.StringProperty()
    date_created = ndb.DateTimeProperty()
    prospect = ndb.BooleanProperty(default=False)
    myself = ndb.BooleanProperty(default=False)
    
    def make_to_dict(self):

        to_dict = {}

        to_dict['name'] = self.name
        to_dict['ref'] = self.ref
        to_dict['bp'] = self.bp
        to_dict['adresse'] = self.adresse
        to_dict['ville'] = self.ville
        to_dict['pays'] = self.pays
        to_dict['email'] = self.email
        to_dict['phone'] = self.phone
        to_dict['date_created'] = str(self.date_created)
        to_dict['prospect'] = self.prospect
        to_dict['myself'] = self.myself

        contacts = Contact.query(
            Contact.client_id == self.key
        )

        contact = [{
            'first_name': conta.first_name,
            'last_name': conta.last_name,
            'email': conta.email,
            'phone1': conta.phone1,
            'phone2': conta.phone2
        } for conta in contacts]

        to_dict['contacts'] = contact

        from ..budget.models_budget import ClientBudget
        budgets = ClientBudget.query(
            ClientBudget.client_id == self.key
        )

        budget = [{
            'montant': bud.montant,
            'date_app': str(bud.date_app)
        } for bud in budgets]
        to_dict['budgets'] = budget

        return to_dict


class Contact(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone1 = ndb.StringProperty()
    phone2 = ndb.StringProperty()
    client_id = ndb.KeyProperty(kind=Client)