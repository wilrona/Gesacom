__author__ = 'Ronald'

from ...modules import *
from models_domaine import Domaine, Service
from forms_domaine import FormDomaine, FormService

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('domaine', __name__)


@prefix.route('/domaine')
@login_required
@roles_required([('super_admin', 'domaine')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'domaine'
    title_page = 'Parametre - Domaines'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Domaine.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='domaines')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('domaine/index.html', **locals())


@prefix.route('/domaine/edit',  methods=['GET', 'POST'])
@prefix.route('/domaine/edit/<int:domaine_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'domaine')], ['edit'])
def edit(domaine_id=None):

    if domaine_id:
        domaines = Domaine.get_by_id(domaine_id)
        form = FormDomaine(obj=domaines)
        form.id.data = domaine_id
    else:
        domaines = Domaine()
        form = FormDomaine()

    success = False
    if form.validate_on_submit():

        domaines.libelle = form.libelle.data
        domaines.code = form.code.data
        domaines.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('domaine/edit.html', **locals())


@prefix.route('/domaine/delete/<int:domaine_id>')
@login_required
@roles_required([('super_admin', 'domaine')], ['delete'])
def delete(domaine_id):
    from ..projet.models_projet import Projet
    domaines = Domaine.get_by_id(domaine_id)

    dom_projet = Projet.query(
        Projet.domaine_id == domaines.key
    ).count()

    if dom_projet:
        flash('Impossible de supprimer cet element', 'danger')
    else:
        domaines.key.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('domaine.index'))


@prefix.route('/domaine/service/<int:domaine_id>')
@login_required
@roles_required([('super_admin', 'ligne')])
def domaine_service(domaine_id):

    domaines = Domaine.get_by_id(domaine_id)
    data_service = Service.query(
        Service.domaine == domaines.key
    )
    return render_template('domaine/index_ligne.html', **locals())


@prefix.route('/domaine/service/edit/<int:domaine_id>', methods=['GET', 'POST'])
@prefix.route('/domaine/service/edit/<int:domaine_id>/<int:service_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'ligne')], ['edit'])
def domaine_service_edit(domaine_id, service_id=None):

    domaines = Domaine.get_by_id(domaine_id)

    if service_id:
        services = Service.get_by_id(service_id)
        form = FormService(obj=services)
        form.id.data = service_id
    else:
        services = Service()
        form = FormService()

    if form.validate_on_submit():

        services.libelle = form.libelle.data
        services.code = form.code.data
        services.domaine = domaines.key
        services.put()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('domaine.domaine_service', domaine_id=domaine_id))

    return render_template('domaine/edit_ligne.html', **locals())


@prefix.route('/domaine/service/delete/<int:domaine_id>/<int:service_id>')
@login_required
@roles_required([('super_admin', 'ligne')], ['delete'])
def domaine_service_delete(domaine_id, service_id):
    from ..projet.models_projet import Projet

    services = Service.get_by_id(service_id)

    projet = Projet.query(
        Projet.service_id == services.key
    ).count()

    if projet:
        flash('Impossible de supprimer', 'danger')
    else:
        services.key.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('domaine.domaine_service', domaine_id=domaine_id))