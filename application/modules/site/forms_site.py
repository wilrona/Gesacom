__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormSite(wtf.Form):
    libelle = wtf.StringField(label='Nom du site', validators=[validators.Required(message='Champ obligatoire')])