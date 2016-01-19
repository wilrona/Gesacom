__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_domaine import Domaine, Service


def unique_code_validator(form, field):
    code_unique = Domaine.query(
        Domaine.code == field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce code est deja utilise dans le domaine.')
        else:
            code = Domaine.get_by_id(int(form.id.data))
            if code.code != field.data:
                raise wtf.ValidationError('Ce code est deja utilise dans le domaine.')


def unique_code_validator_service(form, field):
    code_unique = Service.query(
        Service.code == field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce code est deja utilise dans les lignes de service.')
        else:
            code = Service.get_by_id(int(form.id.data))
            if code.code != field.data:
                raise wtf.ValidationError('Ce code est deja utilise dans les lignes de service.')


class FormDomaine(wtf.Form):
    id = wtf.HiddenField()
    code = wtf.StringField('code domaine', validators=[validators.Required(message='Champ obligatoire'), unique_code_validator])
    libelle = wtf.StringField(label='Nom du domaine', validators=[validators.Required(message='Champ obligatoire')])


class FormService(wtf.Form):
    id = wtf.HiddenField()
    code = wtf.StringField('code service', validators=[validators.Required(message='Champ obligatoire'), unique_code_validator_service])
    libelle = wtf.StringField(label='Nom du service', validators=[validators.Required(message='Champ obligatoire')])

