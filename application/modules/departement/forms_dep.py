__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormDep(wtf.Form):
    libelle = wtf.StringField(label='Nom du depart.', validators=[validators.Required(message='Champ obligatoire')])