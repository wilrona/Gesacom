__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from application import function
import datetime


class FormUser(wtf.Form):
    matricule = wtf.StringField(label='Matricule :', validators=[validators.Required('Matricule Obligatoire')])
    grade_id = wtf.SelectField(label='Selectionnez un grade :', coerce=int,  validators=[validators.Required('Choix obligatoire')])
    fonction_id = wtf.SelectField(label='Selectionez une fonction :', coerce=int, validators=[validators.Required('Choix obligatoire')])
    site_id = wtf.SelectField(label='Selectionez un site :', coerce=int, validators=[validators.Required('Choix obligatoire')])
    departement_id = wtf.SelectField(label='Selectionez un departement :', coerce=int, validators=[validators.Required('Choix obligatoire')])
    date_start = wtf.DateField(label='A commencer le:', format="%d/%m/%Y")


# formulaire pour le taux horaire
def control_pass_date(form, field):
    date = function.date_convert(field.data)
    if datetime.date.today() > date:
        raise wtf.ValidationError('Appliquez les taux horaires sur une date futur ou actuelle.')


class FormHoraire(wtf.Form):
    date_start = wtf.DateField(label='Date de debut d\'application :', format='%d/%m/%Y', validators=[validators.Required('Champ Obligatoire'), control_pass_date])
    montant = wtf.StringField(label='Montant t/h :', validators=[validators.Required('Champ Obligatoire')])