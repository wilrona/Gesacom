__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from ...modules import *


def verif_facturable(form, field):
    if not form.factu.data and not form.nfactu.data:
        raise wtf.ValidationError('Un frais doit etre soit facturable ou non facturable ou les deux.')


class FormFrais(wtf.Form):
    libelle = wtf.StringField(label='Nom du frais', validators=[validators.Required(message='Champ obligatoire')])
    factu = wtf.BooleanField(label='Facturable ?', validators=[verif_facturable])
    nfactu = wtf.BooleanField(label='Non Facturable ?')


class FormFraisProjet(wtf.Form):
    montant = wtf.FloatField(label='Montant :', validators=[validators.Required('Champ Obligatoire')])
    facturable = wtf.StringField(label='Facturation', validators=[validators.Required('Champ Obligatoire')])
    frais_id = wtf.SelectField(label='Frais applique', coerce=int, validators=[validators.Required('Champ Obligatoire')])


def control_date(form, field):
    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    send_date = function.date_convert(field.data)

    if send_date < function.date_convert(start) or send_date > function.date_convert(end):
        raise wtf.ValidationError('La date doit etre comprise entre '+function.format_date(start, '%d/%m/%Y')+" et "+function.format_date(end, '%d/%m/%Y'))


class FormFraisTache(wtf.Form):
    date = wtf.DateField(label='Date de debut :', format="%d/%m/%Y", validators=[validators.Required('Champ Obligatoire'), control_date])
    description = wtf.TextAreaField(label='Descritpion :', validators=[validators.Required('Champ Obligatoire')])
    montant = wtf.FloatField(label='Montant :', validators=[validators.Required('Champ Obligatoire')])
    frais_projet_id = wtf.SelectField(label='Frais associee', coerce=int,  validators=[validators.Required('Champ Obligatoire')])
    detail_fdt = wtf.SelectField(label='FDT concernee', coerce=int)