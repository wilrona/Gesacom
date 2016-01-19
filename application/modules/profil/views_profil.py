__author__ = 'wilrona'

from ...modules import *

from models_profil import Profil, ProfilRole, Roles
from forms_profil import FormProfil

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('profil', __name__)


@prefix.route('/profil')
@login_required
@roles_required([('super_admin', 'profil')])
def index():
    menu = 'societe'
    submenu = 'roles'
    context = 'profil'
    title_page = 'Gestion des profils'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    datas = Profil.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Profils')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas.fetch(limit=10, offset=offset)

    return render_template('profil/index.html', **locals())


@prefix.route('/profil/edit',  methods=['GET', 'POST'])
@prefix.route('/profil/edit/<int:profil_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(profil_id=None):

    if profil_id:
        profils = Profil.get_by_id(profil_id)
        form = FormProfil(obj=profils)
        form.id.data = profil_id
    else:
        profils = Profil()
        form = FormProfil()

    success = False
    if form.validate_on_submit():

        profils.name = form.name.data
        profils.description = form.description.data
        profils.active = form.active.data
        profils.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('profil/edit.html', **locals())


@prefix.route('/profil/delete/<int:profil_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(profil_id):
    profils = Profil.get_by_id(profil_id)

    profil_role_exist = ProfilRole.query(
        ProfilRole.profil_id == profils.key
    ).count()

    if profil_role_exist:
        flash('Impossible de supprimer de profil car il contient des roles', 'warning')
    else:
        profils.key.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('profil.index'))


@prefix.route('/profil/role/<int:profil_id>',  methods=['GET', 'POST'])
def list(profil_id):

    profil = Profil.get_by_id(profil_id)

    # liste des roles lie au profil en cours
    attrib = ProfilRole.query(
        ProfilRole.profil_id == profil.key
    )
    attrib_list = [role.role_id.get().key.id() for role in attrib]

    # liste des roles lie au profil en cours avec le droit d'edition
    edit = ProfilRole.query(
        ProfilRole.profil_id == profil.key,
        ProfilRole.edit == True
    )
    edit_list = [role.role_id.get().key.id() for role in edit]

    # liste des roles lie au profil en cours avec le droit de modification
    delete = ProfilRole.query(
        ProfilRole.profil_id == profil.key,
        ProfilRole.delete == True
    )
    delete_list = [role.role_id.get().key.id() for role in delete]

    liste_role = []
    data_role = Roles.query(
        Roles.valeur != 'super_admin'
    )

    for role in data_role:
        if not role.parent:
            module = {}
            module['titre'] = role.titre
            enfants = Roles.query(
                Roles.parent == role.key
            )
            module['role'] = []
            for enfant in enfants:
                rol = {}
                rol['id'] = enfant.key.id()
                rol['titre'] = enfant.titre
                rol['action'] = enfant.action
                module['role'].append(rol)
            liste_role.append(module)

    success = False
    if request.method == 'POST':

        form_attrib = request.form.getlist('attrib')
        form_edit = request.form.getlist('edit')
        form_delete = request.form.getlist('delete')
        
        # liste des roles lie au profil et supprimer ce qui ne sont plus attribue
        current_profil_role = ProfilRole.query(
            ProfilRole.profil_id == profil.key
        )
        for current in current_profil_role:
            if current.role_id.get().key.id() not in form_attrib:
                current.key.delete()

        # Insertion des roles et authorisation en provenance du formulaire
        for attrib in form_attrib:

            role_form = Roles.get_by_id(int(attrib))

            profil_role_exist = ProfilRole.query(
                ProfilRole.role_id == role_form.key,
                ProfilRole.profil_id == profil.key
            ).get()

            if profil_role_exist:
                if attrib in form_edit:
                    profil_role_exist.edit = True
                else:
                    profil_role_exist.edit = False

                if attrib in form_delete:
                    profil_role_exist.delete = True
                else:
                    profil_role_exist.delete = False

                profil_role_exist.put()
            else:
                profil_role_create = ProfilRole()
                profil_role_create.role_id = role_form.key
                profil_role_create.profil_id = profil.key
                if attrib in form_edit:
                    profil_role_create.edit = True
                else:
                    profil_role_create.edit = False

                if attrib in form_delete:
                    profil_role_create.delete = True
                else:
                    profil_role_create.delete = False

                profil_role_create.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('profil/list.html', **locals())



