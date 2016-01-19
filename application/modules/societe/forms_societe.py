__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators


class FormSociete(wtf.Form):
    name = wtf.StringField(label='Nom de la societe :', validators=[validators.Required(message='Champs Obligatoire')])
    bp = wtf.StringField(label='Boite Postal :', validators=[validators.Required(message='Champs Obligatoire')])
    adress = wtf.StringField(label='Adresse :', validators=[validators.Required(message='Champs Obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required(message='Champs Obligatoire')])
    pays = wtf.StringField(label='Pays :', validators=[validators.Required(message='Champs Obligatoire')])
    phone = wtf.StringField(label='Numero Telephone :', validators=[validators.Required(message='Champs Obligatoire')])
    capital = wtf.StringField(label='Capital social :')
    numcontr = wtf.StringField(label='Numero du contribuable', validators=[validators.Required(message='Champs Obligatoire')])
    registcom = wtf.StringField(label='Registre du commerce')
    email = wtf.StringField(label='Adresse mail', validators=[validators.Required(message='Champs Obligatoire'), validators.Email('Email invalide')])
    siteweb = wtf.StringField(label='Site Web')
    slogan = wtf.StringField(label='Slogan/Breve description')
    typEnt = wtf.StringField(label='Selectionnez le type', validators=[validators.Required(message='Champs Obligatoire')])