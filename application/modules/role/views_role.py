__author__ = 'wilrona'

from ...modules import *
from ..role.models_role import Roles
from forms_role import FormRole


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('role', __name__)


@prefix.route('/role', methods=['GET', 'POST'])
def index():
    menu = 'societe'
    submenu = 'roles'
    context = 'role'
    title_page = 'Gestion des roles'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    datas = Roles.query(
        Roles.valeur != 'super_admin',
        Roles.parent == None
    )
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Roles')

    return render_template('role/index.html', **locals())


@prefix.route('/role/edit/<int:role_id>',  methods=['GET', 'POST'])
@login_required
def edit(role_id):

    roles = Roles.get_by_id(role_id)
    form = FormRole(obj=roles)

    success = False
    if form.validate_on_submit():

        roles.description = form.description.data
        roles.active = form.active.data
        roles.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('role/edit.html', **locals())


@prefix.route('/role/list/<int:role_id>',  methods=['GET', 'POST'])
@login_required
def list(role_id):

    module = Roles.get_by_id(role_id)
    roles = Roles.query(
        Roles.parent == module.key
    )

    return render_template('role/list.html', **locals())


@prefix.route('/role/generate')
def generate():

    for mod in global_role:

        module_exite = Roles.query(
            Roles.valeur == mod['valeur']
        )

        if not module_exite.count():
            module = Roles()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.put()
        else:
            module = module_exite.get()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.put()

        for rol in mod['role']:

            role_exist = Roles.query(
                Roles.valeur == rol['valeur']
            )

            if not role_exist.count():
                role = Roles()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.put()
            else:
                role = role_exist.get()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.put()

    flash(u' All Role generated.', 'success')
    return redirect(url_for('role.index'))

