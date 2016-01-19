__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_client import Client


def unique_email_validator(form, field):
    """ email must be unique"""
    user_manager = Client.query(
        Client.email == field.data
    ).count()
    if user_manager:
        if not form.id.data:
            raise wtf.ValidationError('Cette adresse email existant.')
        else:
            use = Client.get_by_id(int(form.id.data))
            if use.email != field.data:
                raise wtf.ValidationError('Cette adresse email existant.')


def unique_reference(form, field):
    if len(field.data) > 3:
        raise wtf.ValidationError('Pas plus de 03 caracteres pour une reference.')
    else:
        client = Client.query(
            Client.ref == field.data
        ).count()
        if client:
            if not form.id.data:
                raise wtf.ValidationError('Reference Unique. Il en existe un.')
            else:
                use = Client.get_by_id(int(form.id.data))
                if use.ref != field.data:
                    raise wtf.ValidationError('Reference Unique. Il en existe un.')


class FormClient(wtf.Form):
    name = wtf.StringField(label='Nom du Client :', validators=[validators.Required('Champ Obligatoire')])
    ref = wtf.StringField(label='Ref :', validators=[validators.Required('Champ Obligatoire'), unique_reference])
    bp = wtf.StringField(label='Boite Postal :', validators=[validators.Required('Champ Obligatoire')])
    adresse = wtf.TextAreaField(label='Adresse :', validators=[validators.Required('Champ Obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required('Champ Obligatoire')])
    pays = wtf.StringField(label='Pays :', validators=[validators.Required('Champ Obligatoire')])
    email = wtf.StringField(label='Email :', validators=[validators.Required('Champ Obligatoire'), unique_email_validator, validators.Email('Email invalide')])
    phone = wtf.StringField(label='Telephone :', validators=[validators.Required('Champ Obligatoire')])
    id = wtf.HiddenField()


def numeric(form, field):
    data = field.data
    if not isinstance(data, int) and field.data:
        if not data.isdigit():
            raise wtf.ValidationError('l\'information n\'est pas numerique.')


def client_id_required(form, field):
    if form.contact.data:
        if not field.data:
            raise wtf.ValidationError('Selection du client obligatoire.')


class FormContact(wtf.Form):
    first_name = wtf.StringField(label='Nom du contact :', validators=[validators.Required('Champ Obligatoire')])
    last_name = wtf.StringField(label='Prenon du contact :', validators=[validators.Required('Champ Obligatoire')])
    email = wtf.StringField(label='Adresse Email', validators=[validators.Required('Champ Obligatoire'), validators.Email('Email invalide')])
    phone1 = wtf.StringField(label='Telephone mobile :', validators=[numeric])
    phone2 = wtf.StringField(label='Telephone fixe :', validators=[numeric])
    client_id = wtf.SelectField(label='Client du contact :', coerce=int, validators=[client_id_required])
    contact = wtf.HiddenField(default=None)
