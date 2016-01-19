__author__ = 'Ronald'

from ...modules import *
from models_prest import Prestation
from forms_prest import FormPrestation

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('prestation', __name__)


@prefix.route('/prestation')
@login_required
@roles_required([('super_admin', 'prestation')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'prestation'
    title_page = 'Parametre - Prestations'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    datas = Prestation.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='prestation')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('prestation/index.html', **locals())


@prefix.route('/prestation/edit',  methods=['GET', 'POST'])
@prefix.route('/prestation/edit/<int:prestation_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'prestation')], ['edit'])

def edit(prestation_id=None):

    if prestation_id:
        prestations = Prestation.get_by_id(prestation_id)
        form = FormPrestation(obj=prestations)
        form.id.data = prestations.key.id()
    else:
        prestations = Prestation()
        form = FormPrestation()

    success = False
    if form.validate_on_submit():

        prestations.libelle = form.libelle.data
        prestations.factu = form.factu.data
        prestations.nfactu = form.nfactu.data
        prestations.sigle = form.sigle.data
        prestations.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('prestation/edit.html', **locals())


@prefix.route('/prestation/delete/<int:prestation_id>')
@roles_required([('super_admin', 'prestation')], ['delete'])
def delete(prestation_id):
    prestations = Prestation.get_by_id(prestation_id)
    prestations.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('prestation.index'))