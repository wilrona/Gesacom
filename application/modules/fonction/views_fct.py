__author__ = 'Ronald'

from ...modules import *
from models_fct import Fonction
from forms_fct import FormFonction

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('fonction', __name__)


@prefix.route('/fonction')
@login_required
@roles_required([('super_admin', 'fonction')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'fonction'
    title_page = 'Parametre - Fonctions'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Fonction.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='fonctions')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('fonction/index.html', **locals())


@prefix.route('/fonction/edit',  methods=['GET', 'POST'])
@prefix.route('/fonction/edit/<int:fonction_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'fonction')], ['edit'])
def edit(fonction_id=None):

    if fonction_id:
        grades = Fonction.get_by_id(fonction_id)
        form = FormFonction(obj=grades)
    else:
        grades = Fonction()
        form = FormFonction()

    success = False
    if form.validate_on_submit():

        grades.libelle = form.libelle.data
        grades.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('fonction/edit.html', **locals())


@prefix.route('/fonction/delete/<int:fonction_id>')
@login_required
@roles_required([('super_admin', 'fonction')], ['edit'])
def delete(fonction_id):
    fonctions = Fonction.get_by_id(fonction_id)
    if not fonctions.count():
        fonctions.key.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('fonction.index'))