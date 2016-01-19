__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from lib.flaskext.wtf.html5 import NumberInput
from ...modules import *
from models_tache import Tache


def projet_id_required(form, field):
    if form.contact.data:
        if not field.data:
            raise wtf.ValidationError('Selection du projet obligatoire.')


def controle_date_start(form, field):
    if field.data and not form.id.data:
        date_start = function.date_convert(field.data)
        if datetime.date.today() > date_start:
            raise wtf.ValidationError('La date de debut doit etre >= date en cours')

    if form.id.data and field.data:
        date_start = function.date_convert(field.data)
        tache = Tache.get_by_id(int(form.id.data))
        if tache.date_start > date_start:
            raise wtf.ValidationError('La nouvelle date de debut doit etre >= a la date modifie')


class FormTache(wtf.Form):
    titre = wtf.StringField(label='Nom de la tache :', validators=[validators.Required('Champ Obligatoire')])
    description = wtf.TextAreaField(label='Description :')
    heure = wtf.IntegerField(label='Nombre d\'heure :', default=0, widget=NumberInput(), validators=[validators.Required('Champ Obligatoire')])
    date_start = wtf.DateField(label='Date de debut :', format='%d/%m/%Y', default=datetime.date.today(), validators=[controle_date_start])
    facturable = wtf.StringField(label='Facturation :', validators=[validators.Required('Champ Obligatoire')])
    projet_id = wtf.SelectField(label='Projet :', coerce=int, validators=[projet_id_required])
    user_id = wtf.SelectField(label='Utilisateur :', coerce=int, validators=[validators.Required('Champ Obligatoire')])
    prestation_id = wtf.StringField(label='Prestation :', validators=[validators.Required('Champ Obligatoire')])
    contact = wtf.HiddenField(default=None)
    id = wtf.HiddenField()
