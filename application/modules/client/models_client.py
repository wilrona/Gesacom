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


class Contact(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    phone1 = ndb.StringProperty()
    phone2 = ndb.StringProperty()
    client_id = ndb.KeyProperty(kind=Client)