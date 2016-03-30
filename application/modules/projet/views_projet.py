__author__ = 'Ronald'

from ...modules import *

from models_projet import Projet, Domaine, Service, Users, Client
from forms_projet import FormProjet

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('projet', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'projet')])
def index():
    menu = 'projet'
    submenu = 'tous'
    context = ''
    title_page = 'Projets'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1


    datas = Projet.query(
        Projet.closed == False,
        Projet.suspend == False
    )
    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'suspend':
            datas = Projet.query(
                Projet.closed == False,
                Projet.suspend == True
            )
            small_title = 'en suspend'

        if request.args.get('filtre') == 'cloture':
            datas = Projet.query(
                Projet.closed == True,
                Projet.suspend == False
            )
            small_title = 'clotures'

    pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Projets')

    if datas.count() > 25:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 25
        datas = datas.fetch(limit=25, offset=offset)

    return render_template('projet/index.html', **locals())


@prefix.route('/me')
def me():
    from ..tache.models_tache import Tache
    menu = 'projet'
    submenu = 'my'
    context = ''
    title_page = 'Projets'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    user = Users.get_by_id(int(session.get('user_id')))

    all_tache = []
    for tache in Tache.query(Tache.user_id == user.key):
        if tache.projet_id:
            all_tache.append(tache.projet_id.get().key.id())

    all_projet = []
    all_projet_id = []
    count_projet = 0
    en_cours = Projet.query(
        Projet.closed == False,
        Projet.suspend == False
    )

    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'suspend':
            en_cours = Projet.query(
                Projet.closed == False,
                Projet.suspend == True
            )
            small_title = 'en suspend'

        if request.args.get('filtre') == 'cloture':
            en_cours = Projet.query(
                Projet.closed == True,
                Projet.suspend == False
            )
            small_title = 'clotures'

    # Projet ou l'utilisateur a une tache
    for proj in en_cours:
        if proj.key.id() in all_tache:
            projet = {}
            projet['id'] = proj.key.id()
            projet['code'] = proj.code
            projet['titre'] = proj.titre
            projet['client'] = proj.client_id.get().name
            projet['responsable'] = proj.responsable_id.get().last_name
            projet['responsable_id'] = proj.responsable_id.get().key.id()
            all_projet.append(projet)
            all_projet_id.append(proj.key.id())
            count_projet = count_projet + 1

    responsable = Projet.query(
        Projet.responsable_id == user.key,
        Projet.suspend == False,
        Projet.closed == False
    )

    if request.args.get('filtre') and request.args.get('filtre') is not None:
        if request.args.get('filtre') == 'suspend':
            responsable = Projet.query(
                Projet.responsable_id == user.key,
                Projet.closed == False,
                Projet.suspend == True
            )

        if request.args.get('filtre') == 'cloture':
            responsable = Projet.query(
                Projet.responsable_id == user.key,
                Projet.closed == True,
                Projet.suspend == False
            )
    for projs in responsable:
        if projs.key.id() not in all_projet_id:
            projet = {}
            projet['id'] = proj.key.id()
            projet['code'] = proj.code
            projet['titre'] = proj.titre
            projet['client'] = proj.client_id.get().name
            projet['responsable'] = proj.responsable_id.get().last_name
            projet['responsable_id'] = proj.responsable_id.get().key.id()
            all_projet.append(projet)
            count_projet = count_projet + 1

    pagination = Pagination(css_framework='bootstrap3', page=page, total=count_projet, search=search, record_name='Projet')

    return render_template('projet/me.html', **locals())


@prefix.route('/edit', methods=['GET', 'POST'])
@prefix.route('/edit/<int:projet_id>', methods=['GET', 'POST'])
@login_required
def edit(projet_id=None):
    menu = 'projet'
    submenu = 'projet'
    context = 'information'
    title_page = 'Projets - Edition'

    if projet_id:
        projet = Projet.get_by_id(projet_id)
        form = FormProjet(obj=projet)
        form.domaine_id.data = projet.domaine_id.get().key.id()
        form.service_id.data = projet.service_id.get().key.id()
        form.client_id.data = projet.client_id.get().key.id()
        form.responsable_id.data = projet.responsable_id.get().key.id()
        if projet.prospect_id:
            form.prospect_id.data = projet.prospect_id.get().key.id()
        form.id.data = projet_id

    else:
        projet = Projet()
        form = FormProjet()

    form.domaine_id.choices = [(0, 'Selection du domaine')]
    for domaine in Domaine.query():
        form.domaine_id.choices.append((domaine.key.id(), domaine.libelle))

    service = []
    if projet_id:
        services = Service.query(
            Service.domaine == projet.domaine_id
        )
        prospects = Client.query(
            Client.prospect == True
        )

    if form.domaine_id.data and not projet_id:
        domaine = Domaine.get_by_id(int(form.domaine_id.data))
        services = Service.query(
            Service.domaine == domaine.key
        )

    if not projet_id:
        prospects = Client.query(
            Client.prospect == True
        )


    form.client_id.choices = [(0, 'Selection du client')]
    for client in Client.query(Client.prospect == False):
        form.client_id.choices.append((client.key.id(), client.name))

    form.responsable_id.choices = [(0, 'Selection du responsable')]
    for user in Users.query(Users.email != 'admin@accentcom-cm.com'):
        form.responsable_id.choices.append((user.key.id(), user.first_name+" "+user.last_name))

    if form.validate_on_submit() and current_user.has_roles([('super_admin', 'projet')], ['edit']):

        projet.titre = form.titre.data

        client_code = Client.get_by_id(int(form.client_id.data))
        if not projet_id:
            projet_client = Projet.query(
                Projet.client_id == client_code.key
            ).count()
            projet.code = client_code.ref+""+str(projet_client+1)

        projet.heure = form.heure.data
        projet.montant = float(form.montant.data)
        projet.date_start = function.date_convert(form.date_start.data)
        projet.date_end = function.date_convert(form.date_end.data)
        projet.client_id = client_code.key

        if client_code.myself and int(form.prospect_id.data):
            pros = Client.get_by_id(int(form.prospect_id.data))
            projet.prospect_id = pros.key

        user = Users.get_by_id(int(form.responsable_id.data))
        projet.responsable_id = user.key

        domaine = Domaine.get_by_id(int(form.domaine_id.data))
        projet.domaine_id = domaine.key

        service = Service.get_by_id(int(form.service_id.data))
        projet.service_id = service.key

        projet.facturable = form.facturable.data
        projet.closed = form.closed.data

        projet_id = projet.put()
        flash('Enregistrement effectue avec succes', 'success')
        return redirect(url_for('projet.edit', projet_id=projet_id.id()))

    return render_template('projet/edit.html', **locals())


@prefix.route('/closed/<int:projet_id>')
def closed(projet_id):

    from ..tache.models_tache import Tache
    projet = Projet.get_by_id(projet_id)

    if projet.closed:
        projet.closed = False
        projet.put()
    else:
        tache_exist = Tache.query(
            Tache.projet_id == projet.key
        ).count()

        tache_closed = Tache.query(
            Tache.projet_id == projet.key,
            Tache.closed == True
        ).count()

        if tache_closed == tache_exist:
            projet.closed = True
            projet.put()
        else:
            flash('Impossible de cloturer ce projet car il y\'a des taches non cloturees existantes', 'warning')

    return redirect(url_for('projet.edit', projet_id=projet_id))


@prefix.route('/suspend/<int:projet_id>')
def suspend(projet_id):

    projet = Projet.get_by_id(projet_id)

    if projet.suspend:
        projet.suspend = False
    else:
        projet.suspend = True
    projet.put()

    return redirect(url_for('projet.edit', projet_id=projet_id))


@prefix.route('/delete/<int:projet_id>')
@login_required
@roles_required([('super_admin', 'projet')], ['edit'])
def delete(projet_id):

    from ..tache.models_tache import Tache
    from ..frais.models_frais import FraisProjet

    projet = Projet.get_by_id(projet_id)

    frais = FraisProjet.query(
        FraisProjet.projet_id == projet.key
    ).count()

    tache = Tache.query(
        Tache.projet_id == projet.key
    ).count()

    if frais or tache:
        flash('Impossible de supprimer le projet '+ str(projet.code), 'danger')
    else:
        flash('Suppression effectue avec succes', 'success')
        projet.key.delete()
    return redirect(url_for('projet.index'))


@prefix.route('/service')
@prefix.route('/service/<int:domaine_id>')
def services(domaine_id = None):
    data = {}
    if domaine_id:
        domaine = Domaine.get_by_id(domaine_id)
        service = Service.query(
            Service.domaine == domaine.key
        )
        for ser in service:
            data[str(ser.key.id())] = ser.libelle
    resp = jsonify(data)
    return resp


@prefix.route('/prospect')
@prefix.route('/prospect/<int:client_id>')
def prospects(client_id = None):
    data = {}
    if client_id:
        client = Client.get_by_id(client_id)
        if client.myself:
            clients = Client.query(
                Client.prospect == True
            )
            for cli in clients:
                data[str(cli.key.id())] = cli.name
    resp = jsonify(data)
    return resp

