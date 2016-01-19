__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormCharge(wtf.Form):
    libelle = wtf.StringField(label='Nom de la charge', validators=[validators.Required(message='Champ obligatoire')])