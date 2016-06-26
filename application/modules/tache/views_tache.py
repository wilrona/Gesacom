__author__ = 'Ronald'

from ...modules import *
from ..tache.models_tache import Projet, Tache, Users, Prestation, ndb
from forms_tache import FormTache


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('tache', __name__)
prefix_projet = Blueprint('tache_projet', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'tache')])
def index():
    menu = 'tache'
    submenu = 'tous'
    context = ''
    title_page = 'Taches'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #id Prestatation Ferier, Conge et Absence

    prest_ferier = Prestation.query(Prestation.sigle == 'FER').get()
    prest_conge = Prestation.query(Prestation.sigle == 'CONG').get()
    prest_absence = Prestation.query(Prestation.sigle == 'ABS').get()

    if prest_absence and prest_conge and prest_ferier:

        datas = Tache.query(
            Tache.end == False,
            Tache.closed == False,
            Tache.prestation_id != prest_conge.key,
            Tache.prestation_id != prest_absence.key,
            Tache.prestation_id != prest_ferier.key

        )

        if request.args.get('filtre') and request.args.get('filtre') is not None:

            if request.args.get('filtre') == 'end':
                datas = Tache.query(
                    Tache.end == True,
                    Tache.closed == False,

                    Tache.prestation_id != prest_conge.key,
                    Tache.prestation_id != prest_absence.key,
                    Tache.prestation_id != prest_ferier.key

                )
                small_title = 'terminees'

            if request.args.get('filtre') == 'cloture':
                datas = Tache.query(
                    Tache.closed == True,
                    Tache.end == False,
                    Tache.prestation_id != prest_conge.key,
                    Tache.prestation_id != prest_absence.key,
                    Tache.prestation_id != prest_ferier.key

                )
                small_title = 'cloturees'

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Taches')

        if datas.count() > 25:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 25
            datas = datas.fetch(limit=25, offset=offset)
    else:
        if current_user.has_roles(['prestation']):
            flash('Demandez a l\'administrateur de configurer au mieux les prestations de l\'application', 'warning')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Creer SVP les prestations de conge, absence et ferier', 'warning')
            return redirect(url_for('prestation.index'))

    return render_template('tache/index.html', **locals())


@prefix.route('/me')
def me():
    menu = 'tache'
    submenu = 'my'
    context = ''
    title_page = 'Taches'

    user = Users.get_by_id(int(session.get('user_id')))

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #id Prestatation Ferier, Conge et Absence

    prest_ferier = Prestation.query(Prestation.sigle == 'FER').get()
    prest_conge = Prestation.query(Prestation.sigle == 'CONG').get()
    prest_absence = Prestation.query(Prestation.sigle == 'ABS').get()

    if prest_absence and prest_conge and prest_ferier:

        datas = Tache.query(
            Tache.user_id == user.key,
            Tache.end == False,
            Tache.closed == False,
            Tache.prestation_id != prest_conge.key,
            Tache.prestation_id != prest_absence.key,
            Tache.prestation_id != prest_ferier.key

        )

        if request.args.get('filtre') and request.args.get('filtre') is not None:
            if request.args.get('filtre') == 'end':
                datas = Tache.query(
                    Tache.end == True,
                    Tache.closed == False,
                    Tache.user_id == user.key,

                    Tache.prestation_id != prest_conge.key,
                    Tache.prestation_id != prest_absence.key,
                    Tache.prestation_id != prest_ferier.key

                )
                small_title = 'terminees'

            if request.args.get('filtre') == 'cloture':
                datas = Tache.query(
                    Tache.closed == True,
                    Tache.end == True,
                    Tache.user_id == user.key,
                    Tache.prestation_id != prest_conge.key,
                    Tache.prestation_id != prest_absence.key,
                    Tache.prestation_id != prest_ferier.key

                )
                small_title = 'cloturees'

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Taches')

        if datas.count() > 25:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 25
            datas = datas.fetch(limit=25, offset=offset)

    else:
        flash('Demandez a l\'administrateur de configurer au mieux les prestations de l\'application', 'warning')
        return redirect(url_for('dashboard.index'))

    return render_template('tache/me.html', **locals())


@prefix.route('/edit', methods=['GET', 'POST'])
@prefix.route('/edit/<int:tache_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'tache')], ['edit'])
def edit(tache_id=None):
    hors_projet = False
    if tache_id:
        tache = Tache.get_by_id(tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = tache.user_id.get().key.id()
        form.prestation_id.data = tache.prestation_id.get().key.id()
        form.projet_id.data = tache.projet_id.get().key.id()
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = tache.key.id()
    else:
        tache = Tache()
        form = FormTache()
    form.contact.data = "contact"


    form.projet_id.choices = [(0, 'Selectionnez un projet')]
    for projet in Projet.query(Projet.closed == False):
        form.projet_id.choices.append((projet.key.id(), projet.titre))

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.query(Users.email != 'admin@accentcom-cm.com'):
        form.user_id.choices.append((user.key.id(), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.get_by_id(int(form.prestation_id.data))
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    if not tache_id:
        list_prestation = Prestation.query(
                Prestation.sigle != None,
                Prestation.sigle != 'CONG',
                Prestation.sigle != 'ABS',
                Prestation.sigle != 'FER'
        )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = form.heure.data

        user = Users.get_by_id(int(form.user_id.data))
        tache.user_id = user.key

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.get_by_id(int(form.prestation_id.data))
        tache.prestation_id = prestation.key

        projet = Projet.get_by_id(int(form.projet_id.data))
        tache.projet_id = projet.key

        correct = True
        if form.id.data and tache_id:
            if function.date_convert(form.date_start.data) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = function.date_convert(form.date_start.data)
        else:
            tache.date_start = function.date_convert(form.date_start.data)

        ## Controle de la somme des heures par rapport au projet
        if correct:
            heure = projet.heure
            taches = Tache.query(Tache.projet_id == projet.key)
            heure_total = 0
            for tache_heure in taches:
                heure_total += tache_heure.heure

            heure_total += form.heure.data
            heure_restant = heure - heure_total
            if heure_restant < 0:
                form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet')
            else:
                tache.put()
                success = True

    return render_template('tache/edit.html', **locals())

@prefix.route('/no_projet/edit', methods=['GET', 'POST'])
@prefix.route('/no_projet/edit/<int:tache_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'tache')], ['edit'])
def hors_projet(tache_id=None):
    hors_projet = True
    if tache_id:
        tache = Tache.get_by_id(tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = tache.user_id.get().key.id()
        form.prestation_id.data = tache.prestation_id.get().key.id()
        # form.projet_id.data = tache.projet_id.get().key.id()
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = tache.key.id()
    else:
        tache = Tache()
        form = FormTache()
    # form.contact.data = "contact"


    form.projet_id.choices = [(0, 'Selectionnez un projet')]
    for projet in Projet.query(Projet.closed == False):
        form.projet_id.choices.append((projet.key.id(), projet.titre))

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.query(Users.email != 'admin@accentcom-cm.com'):
        form.user_id.choices.append((user.key.id(), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.get_by_id(int(form.prestation_id.data))
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    if not tache_id:
        list_prestation = Prestation.query(
            Prestation.sigle != None,
            Prestation.sigle != 'CONG',
            Prestation.sigle != 'ABS',
            Prestation.sigle != 'FER'
        )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = form.heure.data

        user = Users.get_by_id(int(form.user_id.data))
        tache.user_id = user.key

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.get_by_id(int(form.prestation_id.data))
        tache.prestation_id = prestation.key
        #
        # projet = Projet.get_by_id(int(form.projet_id.data))
        #
        # tache.projet_id = projet.key

        correct = True
        if form.id.data and tache_id:
            if function.date_convert(form.date_start.data) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = function.date_convert(form.date_start.data)
        else:
            tache.date_start = function.date_convert(form.date_start.data)

        ## Controle de la somme des heures par rapport au projet
        # if correct:
        #     heure = projet.heure
        #     taches = Tache.query(Tache.projet_id == projet.key)
        #     heure_total = 0
        #     for tache_heure in taches:
        #         heure_total += tache_heure.heure
        #
        #     heure_total += form.heure.data
        #     heure_restant = heure - heure_total
        #     if heure_restant < 0:
        #         form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet')
        #     else:
        if correct:
            tache.put()
            success = True

    return render_template('tache/edit.html', **locals())


@prefix.route('/delete/<int:tache_id>')
@login_required
def delete(tache_id):
    from ..temps.models_temps import Temps

    tache = Tache.get_by_id(tache_id)

    projet_id = tache.projet_id.get().key.id()

    feuille_temps = Temps.query(
        Temps.tache_id == tache.key
    ).count()
    if feuille_temps:
        flash('Impossible de supprimer l\'element ', 'danger')
    else:
        flash('Suppression reussie', 'success')
        tache.key.delete()
    return redirect(url_for('tache_projet.index', projet_id=projet_id))


@prefix.route('/detail/<int:tache_id>')
@login_required
def detail(tache_id):

    menu = 'tache'
    submenu = 'tache'
    context = 'information'
    title_page = 'Taches - Details'

    tache = Tache.get_by_id(tache_id)

    return render_template('tache/detail.html', **locals())


@prefix.route('/end/<int:tache_id>')
@login_required
def end(tache_id):

    tache = Tache.get_by_id(tache_id)

    if tache.end:
        tache.end = False
        tache.put()
    else:
        tache.end = True
        if not tache.projet_id:
            from ..temps.models_temps import Temps
            day = datetime.date.today().strftime('%d/%m/%Y')
            dt = datetime.datetime.strptime(day, '%d/%m/%Y')
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)

            temps_count = Temps.query(
                Temps.date_start == start,
                Temps.date_end == end,
                Temps.tache_id == tache.key
            ).count()

            if temps_count:
               flash('Vous ne pouvez pas supprimer cette tache car elle comporte des feuilles de temps', 'warning')
            else:
                tache.closed = True
                tache.put()
        else:

            tache.put()
    return redirect(url_for('tache.detail', tache_id=tache_id))


@prefix.route('/closed/<int:tache_id>')
@login_required
def closed(tache_id):
    tache = Tache.get_by_id(tache_id)
    if tache.closed:
        tache.closed = False
    else:
        tache.closed = True
    tache.put()
    return redirect(url_for('tache_projet.index', tache_id=tache.projet_id.get().key.id()))


## LISTE DES TACHES D'UN PROJET
@prefix_projet.route('/tache/<int:projet_id>')
@login_required
def index(projet_id):
    menu = 'projet'
    submenu = 'projet'
    context = 'tache'
    title_page = 'Projets - Taches'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    projet = Projet.get_by_id(projet_id)
    datas = Tache.query(Tache.projet_id == projet.key)
    pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Taches')

    if datas.count() > 25:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 25
        datas = datas.fetch(limit=25, offset=offset)

    return render_template('tache/tache_projet.html', **locals())


## EDITION D'UNE TACHE DEPUIS UN PROJET
@prefix_projet.route('/tache/edit/<int:projet_id>', methods=['GET', 'POST'])
@prefix_projet.route('/tache/edit/<int:projet_id>/<int:tache_id>', methods=['GET', 'POST'])
@login_required
def edit(projet_id, tache_id=None):

    projet = Projet.get_by_id(projet_id)

    if tache_id:
        tache = Tache.get_by_id(tache_id)
        form = FormTache(obj=tache)
        form.user_id.data = tache.user_id.get().key.id()
        form.prestation_id.data = tache.prestation_id.get().key.id()
        form.projet_id.data = tache.projet_id.get().key.id()
        if tache.facturable:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
        form.id.data = tache.key.id()
    else:
        tache = Tache()
        form = FormTache()


    form.projet_id.choices = [(projet.key.id(), projet.titre)]

    form.user_id.choices = [(0, 'Selectionnez l\'utilisateur')]
    for user in Users.query(Users.email != 'admin@accentcom-cm.com'):
        form.user_id.choices.append((user.key.id(), user.first_name+" "+user.last_name))

    if form.prestation_id.data:
        prest = Prestation.get_by_id(int(form.prestation_id.data))
        list_factu = {}
        if prest.nfactu:
            list_factu[2] = 'Non Facturable'
        if prest.factu:
            list_factu[1] = 'Facturable'

    list_prestation = Prestation.query(
        Prestation.sigle != None,
        Prestation.sigle != 'CONG',
        Prestation.sigle != 'ABS',
        Prestation.sigle != 'FER'
    )

    success = False
    if form.validate_on_submit():
        tache.titre = form.titre.data
        tache.description = form.description.data
        tache.heure = form.heure.data

        user = Users.get_by_id(int(form.user_id.data))
        tache.user_id = user.key

        if form.facturable.data == '2':
            tache.facturable = False
        if form.facturable.data == '1':
            tache.facturable = True

        prestation = Prestation.get_by_id(int(form.prestation_id.data))
        tache.prestation_id = prestation.key
        tache.projet_id = projet.key

        correct = True
        if form.id.data and tache_id:
            if function.date_convert(form.date_start.data) < tache.date_start:
                form.date_start.errors.append('La date de debut ne peut etre anterieure a la precedente')
                correct = False
            else:
                tache.date_start = function.date_convert(form.date_start.data)
        else:
            tache.date_start = function.date_convert(form.date_start.data)

        ## Controle de la somme des heures par rapport au projet
        if correct:
            heure = projet.heure
            taches = Tache.query(Tache.projet_id == projet.key)
            heure_total = 0
            for tache_heure in taches:
                heure_total += tache_heure.heure

            heure_total += form.heure.data
            heure_restant = heure - heure_total
            if heure_restant < 0:
                form.heure.errors.append('Heure ventillee superieur a l\'heure total du projet' + str(heure_restant))
            else:
                tache.put()
                success = True

    return render_template('tache/tache_projet_edit.html', **locals())


@prefix_projet.route('/prestation')
@prefix_projet.route('/prestation/<int:prestation_id>')
def facturations(prestation_id = None):
    data = {}
    data['fact'] = 0
    data['nfact'] = 0
    if prestation_id:
        prestation = Prestation.get_by_id(prestation_id)
        if prestation.factu:
            data['fact'] = 1
        if prestation.nfactu:
            data['nfact'] = 1
    resp = jsonify(data)
    return resp


# cron temps remplit sur une tache
@prefix.route('/fdt_tache')
def fdt_tache():
    from ..temps.models_temps import Temps, Tache, DetailTemps

    for tache in Tache.query():
        total = 0.0
        for temps in Temps.query(Temps.tache_id == tache.key):
            details = DetailTemps.query(
                DetailTemps.temps_id == temps.key
            )
            for detail in details:
                total += detail.conversion

        tache.detail_heure = total
        tache.put()

    return render_template('401.html')


@prefix.route('/montant_projet_fdt')
def montant_projet_fdt():
    from ..tache.models_tache import Tache, Projet

    for projet in Projet.query():

        tache_projet = Tache.query(
            Tache.projet_id == projet.key
        )

        total = 0.0
        for tache in tache_projet:
            if tache.prestation_sigle() == 'PRO' and tache.facturable:
                user_taux = tache.user_id.get().tauxH
                time = tache.detail_heure

                pre_total = user_taux * time

                total += pre_total

        projet.montant_projet_fdt = total
        projet.put()

    return render_template('401.html')

