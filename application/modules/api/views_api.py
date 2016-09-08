__author__ = 'Ronald'


from ...modules import *
from ..role.models_role import Roles
from ..profil.models_profil import Profil
from ..societe.models_societe import Societe
from ..site.models_site import Site
from ..departement.models_dep import Departement
from ..fonction.models_fct import Fonction
from ..grade.models_grade import Grade
from ..prestation.models_prest import Prestation
from ..frais.models_frais import Frais
from ..charge.models_charge import Charge
from ..client.models_client import Client
from ..domaine.models_domaine import Domaine
from ..user.models_user import Users
from ..budget.models_budget import Budget
from ..projet.models_projet import Projet
from ..tache.models_tache import Tache
from ..temps.models_temps import Temps


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('api', __name__)


@prefix.route('/roles')
def roles():
    datas = {'status': 200, 'data': []}
    for data in Roles.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/profil')
def profil():
    datas = {'status': 200, 'data': []}
    for data in Profil.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/societe')
def societe():
    datas = {'status': 200, 'data': []}
    for data in Societe.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/site')
def site():
    datas = {'status': 200, 'data': []}
    for data in Site.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/departement')
def departement():
    datas = {'status': 200, 'data': []}
    for data in Departement.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/fonction')
def fonction():
    datas = {'status': 200, 'data': []}
    for data in Fonction.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/grade')
def grade():
    datas = {'status': 200, 'data': []}
    for data in Grade.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/prestation')
def prestation():
    datas = {'status': 200, 'data': []}
    for data in Prestation.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/frais')
def frais():
    datas = {'status': 200, 'data': []}
    for data in Frais.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/charge')
def charge():
    datas = {'status': 200, 'data': []}
    for data in Charge.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/client')
def client():
    datas = {'status': 200, 'data': []}
    for data in Client.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp

@prefix.route('/domaine')
def domaine():
    datas = {'status': 200, 'data': []}
    for data in Domaine.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp

@prefix.route('/user')
def user():
    datas = {'status': 200, 'data': []}
    for data in Users.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/budget')
def budget():
    datas = {'status': 200, 'data': []}
    for data in Budget.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/projet')
def projet():
    datas = {'status': 200, 'data': []}
    for data in Projet.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/tache')
def tache():
    datas = {'status': 200, 'data': []}
    for data in Tache.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp


@prefix.route('/temps')
def temps():
    datas = {'status': 200, 'data': []}
    for data in Temps.query():
        datas['data'].append(data.make_to_dict())
    resp = jsonify(datas)
    return resp