__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from lib.flaskext.wtf.html5 import NumberInput
from ...modules import *
from models_projet import Projet, Client


def controle_date_end(form, field):
    date_start = function.date_convert(form.date_start.data)
    date_end = function.date_convert(field.data)
    if date_end < date_start:
        raise wtf.ValidationError('La date de fin doit etre > la date de debut')


def controle_date_start(form, field):
    date_start = function.date_convert(field.data)
    if datetime.date.today() > date_start and not form.id.data:
        raise wtf.ValidationError('La date de debut doit etre >= date en cours')

    if form.id.data:
        projet = Projet.get_by_id(int(form.id.data))
        if projet.date_start > date_start:
            raise wtf.ValidationError('La nouvelle date de debut doit etre >= a la date modifie')


class FormProjet(wtf.Form):
    titre = wtf.StringField(label='Nom du projet', validators=[validators.Required('Champ Obligatoire')])
    heure = wtf.IntegerField(label='Nombre d\'heure', default=0, widget=NumberInput(),validators=[validators.Required('Champ Obligatoire')])
    montant = wtf.FloatField(label='Montant vendu', validators=[validators.Required('Champ Obligatoire')])
    date_start = wtf.DateField(label='Date de debut', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), controle_date_start])
    date_end = wtf.DateField(label='Date de fin', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), controle_date_end])
    facturable = wtf.BooleanField(label='Facturable ?')
    domaine_id = wtf.SelectField(label='Domaine ', coerce=int, validators=[validators.Required('Champ Obligatoire')])
    client_id = wtf.SelectField(label='Client', coerce=int, validators=[validators.Required('Champ Obligatoire')])
    service_id = wtf.StringField(label='Ligne de service', validators=[validators.Required('Champ Obligatoire')])
    prospect_id = wtf.StringField(label='Pour le compte de')
    responsable_id = wtf.SelectField(label='Responsable', coerce=int, validators=[validators.Required('Champ Obligatoire')])
    closed = wtf.BooleanField(label='Cloturer ?')
    id = wtf.HiddenField()
