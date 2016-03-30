__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from lib.flaskext.wtf.html5 import NumberInput


def verif_dispobilite(form, field):
    dispo = float(field.data) - float(form.administration.data)
    dispo -= float(form.production.data)
    dispo -= float(form.formation.data)
    dispo -= float(form.developpement.data)
    if dispo > 0:
        raise wtf.ValidationError('La somme des heures de prestation n\'est pas egale aux heures disponibles')
    if dispo < 0:
        raise wtf.ValidationError('La somme des heures de prestation est superieure aux heures disponibles '+str(dispo))


class FormBudget(wtf.Form):
    disponible = wtf.FloatField(label='Temps Disponible :', default=0, validators=[validators.NumberRange(min=1, message='La disponibilite doit etre plus de 0'), verif_dispobilite])
    administration = wtf.FloatField(label='Administration (en H) :', default=0,  validators=[validators.NumberRange(min=0, message='Valeur Minimal 0')])
    production = wtf.FloatField(label='Production (en H) :', default=0,  validators=[validators.NumberRange(min=0, message='Valeur Minimal 0')])
    formation = wtf.FloatField(label='Formation (en H) :', default=0,  validators=[validators.NumberRange(min=0, message='Valeur Minimal 0')])
    developpement = wtf.FloatField(label='Developpement (en H) :', default=0,  validators=[validators.NumberRange(min=0, message='Valeur Minimal 0')])