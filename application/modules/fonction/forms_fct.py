__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormFonction(wtf.Form):
    libelle = wtf.StringField(label='Nom fonction', validators=[validators.Required(message='Champ obligatoire')])