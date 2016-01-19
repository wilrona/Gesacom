__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators

class FormGrade(wtf.Form):
    libelle = wtf.StringField(label='Nom du grade', validators=[validators.Required(message='Champ obligatoire')])