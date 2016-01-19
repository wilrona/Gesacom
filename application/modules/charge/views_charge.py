__author__ = 'Ronald'

from ...modules import *
from models_charge import Charge
from forms_charge import FormCharge
from ..societe.models_societe import Societe

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('charge', __name__)


@prefix.route('/charge')
@login_required
@roles_required([('super_admin', 'charge')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'charge'
    title_page = 'Parametre - Charges/Impots'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Charge.query()

    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Charges')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10

        datas = Charge.query().fetch(limit=10, offset=offset)

    return render_template('charge/index.html', **locals())


@prefix.route('/charge/edit',  methods=['GET', 'POST'])
@prefix.route('/charge/edit/<int:charge_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(charge_id=None):

    if charge_id:
        charges = Charge.get_by_id(charge_id)
        form = FormCharge(obj=charges)
    else:
        charges = Charge()
        form = FormCharge()

    success = False
    if form.validate_on_submit():
        entreprise = Societe.query().get()

        charges.libelle = form.libelle.data
        charges.societe = entreprise.key
        charges.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('charge/edit.html', **locals())


@prefix.route('/charge/delete/<int:charge_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(charge_id):
    charges = Charge.get_by_id(charge_id)

    from ..budget.models_budget import ChargeBudget
    bugdet = ChargeBudget.query(
        ChargeBudget.charge_id == charges.key
    ).count()

    if bugdet:
        flash('Impossible de supprimer cet element', 'warning')
    else:
        charges.key.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('charge.index'))