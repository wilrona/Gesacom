__author__ = 'Ronald'

from ...modules import *
from models_frais import Frais, FraisProjet, Projet
from forms_frais import FormFrais, FormFraisProjet, FormFraisTache
from ..temps.models_temps import Temps, Tache, DetailFrais, DetailTemps

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('frais', __name__)
prefix_projet = Blueprint('frais_projet', __name__)
prefix_tache = Blueprint('frais_tache', __name__)


@prefix.route('/frais')
@login_required
@roles_required([('super_admin', 'frais')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'frais'
    title_page = 'Parametre - Frais'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Frais.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='frais')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('frais/index.html', **locals())


@prefix.route('/frais/edit',  methods=['GET', 'POST'])
@prefix.route('/frais/edit/<int:frais_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'frais')], ['edit'])
def edit(frais_id=None):

    if frais_id:
        fraiss = Frais.get_by_id(frais_id)
        form = FormFrais(obj=fraiss)
    else:
        fraiss = Frais()
        form = FormFrais()

    success = False
    if form.validate_on_submit():

        fraiss.libelle = form.libelle.data
        fraiss.factu = form.factu.data
        fraiss.nfactu = form.nfactu.data
        fraiss.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('frais/edit.html', **locals())


@prefix.route('/frais/delete/<int:frais_id>')
@login_required
@roles_required([('super_admin', 'frais')], ['delete'])
def delete(frais_id):
    fraiss = Frais.get_by_id(frais_id)

    frais_projet = FraisProjet.query(
        FraisProjet.frais_id == fraiss.key
    ).count()

    if frais_projet:
        flash('Impossible de supprimer cet element', 'danger')
    else:
        fraiss.key.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('frais.index'))


# LISTE DES FRAIS DANS UN PROJET
@prefix_projet.route('/frais/<int:projet_id>')
@login_required
def index(projet_id):
    menu = 'projet'
    submenu = 'projet'
    context = 'frais'
    title_page = 'Projets - Frais'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    projet = Projet.get_by_id(projet_id)
    datas = FraisProjet.query(FraisProjet.projet_id == projet.key)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Projets')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('frais/frais_projet.html', **locals())


@prefix_projet.route('/frais/edit/<int:projet_id>',  methods=['GET', 'POST'])
@prefix_projet.route('/frais/edit/<int:projet_id>/<int:frais_projet_id>',  methods=['GET', 'POST'])
@login_required
def edit(projet_id, frais_projet_id=None):

    projet = Projet.get_by_id(projet_id)
    if frais_projet_id:
        frais_projet = FraisProjet.get_by_id(frais_projet_id)
        form = FormFraisProjet(obj=frais_projet)
        form.frais_id.data = frais_projet.frais_id.get().key.id()
        if frais_projet.frais_id.get().factu:
            form.facturable.data = '1'
        else:
            form.facturable.data = '2'
    else:
        frais_projet = FraisProjet()
        form = FormFraisProjet()

    form.frais_id.choices = [(0, 'Selectionnez un frais')]
    for frais in Frais.query():
        form.frais_id.choices.append((frais.key.id(), frais.libelle))

    if form.frais_id.data:
        frais = Frais.get_by_id(int(form.frais_id.data))
        list_factu = {}
        if frais.nfactu:
            list_factu[2] = 'Non Facturable'
        if frais.factu:
            list_factu[1] = 'Facturable'

    success = False
    if form.validate_on_submit():

        frais_projet.projet_id = projet.key

        frais = Frais.get_by_id(int(form.frais_id.data))
        frais_projet.frais_id = frais.key

        if form.facturable.data == '2':
            frais_projet.facturable = False
        if form.facturable.data == '1':
            frais_projet.facturable = True

        frais_projet.montant = form.montant.data
        frais_projet.put()

        success = True

    return render_template('frais/frais_projet_edit.html', **locals())

@prefix_projet.route('/frais/delete/<int:frais_projet_id>')
@login_required
def delete(frais_projet_id):
    frais = FraisProjet.get_by_id(frais_projet_id)

    projet_id = frais.projet_id.get().key.id()

    frais_tache = DetailFrais.query(
        DetailFrais.frais_projet_id == frais.key
    )

    if frais_tache.count():
        flash('Impossible de supprimer', 'danger')
    else:
        flash('Enregistrement effectue avec succes', 'success')
        frais.key.delete()
    return redirect(url_for('frais_projet.index', projet_id=projet_id))



@prefix_projet.route('/facturation')
@prefix_projet.route('/facturation/<int:frais_id>')
def facturations(frais_id = None):
    data = {}
    data['fact'] = 0
    data['nfact'] = 0
    if frais_id:
        frais = Frais.get_by_id(frais_id)
        if frais.factu:
            data['fact'] = 1
        if frais.nfactu:
            data['nfact'] = 1
    resp = jsonify(data)
    return resp


@prefix_tache.route('/frais/<int:tache_id>/')
@login_required
def index(tache_id):
    menu = 'tache'
    submenu = 'tache'
    context = 'frais'
    title_page = 'Taches - Details - Frais'

    tache = Tache.get_by_id(tache_id)

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    temps = Temps.query(
        Temps.tache_id == tache.key,
        Temps.date_start == start,
        Temps.date_end == end
    ).get()

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = []
    pagination = None
    if temps:
        datas = DetailFrais.query(DetailFrais.temps_id == temps.key)

        pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Frais de la tache')
        if datas.count() > 10:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 10
            datas = datas.fetch(limit=10, offset=offset)

    return render_template('frais/frais_tache.html', **locals())


@prefix_tache.route('/frais/edit/<int:tache_id>', methods=['GET', 'POST'])
@prefix_tache.route('/frais/edit/<int:tache_id>/<int:detail_frais_id>', methods=['GET', 'POST'])
@login_required
def edit(tache_id, detail_frais_id=None):

    tache = Tache.get_by_id(tache_id)

    if detail_frais_id:
        detail_frais = DetailFrais.get_by_id(detail_frais_id)
        form = FormFraisTache(obj=detail_frais)
        form.frais_projet_id.data = detail_frais.frais_projet_id.get().key.id()
        if detail_frais.detail_fdt:
            form.detail_fdt.data = detail_frais.detail_fdt.get().key.id()
    else:
        detail_frais = DetailFrais()
        form = FormFraisTache()

    form.frais_projet_id.choices = [(0, 'Selectionnez le frais applique')]
    for frais in FraisProjet.query(FraisProjet.projet_id == tache.projet_id):
        form.frais_projet_id.choices.append((frais.key.id(), frais.frais_id.get().libelle))

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)


    temps = Temps.query(
        Temps.tache_id == tache.key,
        Temps.date_start == start,
        Temps.date_end == end
    ).get()

    form.detail_fdt.choices = [(0, 'Selectionnez la FDT concernee')]
    if temps:
        for frais in DetailTemps.query(DetailTemps.temps_id == temps.key):
            form.detail_fdt.choices.append((frais.key.id(), frais.description))

    success = False
    if form.validate_on_submit():

        detail_frais.date = function.date_convert(form.date.data)
        detail_frais.montant = form.montant.data
        detail_frais.description = form.description.data

        frais_projet = FraisProjet.get_by_id(form.frais_projet_id.data)
        detail_frais.frais_projet_id = frais_projet.key

        if form.detail_fdt.data:
            details_DFT = DetailTemps.get_by_id(form.detail_fdt.data)
            detail_frais.detail_fdt = details_DFT.key

        if temps:
            detail_frais.temps_id = temps.key
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = function.date_convert(start)
            temps.date_end = function.date_convert(end)
            temps.tache_id = tache.key
            time = temps.put()
            detail_frais.temps_id = time

        detail_frais.put()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('frais/frais_tache_edit.html', **locals())


@prefix_tache.route('/frais/delete/<int:detail_frais_id>')
@login_required
def delete(detail_frais_id):

    # Information du details des frais du FDT
    details_temps = DetailFrais.get_by_id(detail_frais_id)

    # Recuperation des details des frais correspondant a la meme FDT du frais a supprimer
    frais_detail_count = DetailFrais.query(
        details_temps.temps_id == details_temps.temps_id
    )

    temps_detail_count = DetailFrais.query(
        DetailFrais.temps_id == details_temps.temps_id
    )

    # id de la feuille de temps de la semaine
    temps_id = details_temps.temps_id.get().key.id()

    # id de la tache de la semaine
    tache_id = Temps.get_by_id(temps_id)
    tache_id = tache_id.tache_id.get().key.id()

    # if il n'existe plus de details temps correspondant a la FDT de la semaine, on le supprime.
    if not frais_detail_count.count() and not temps_detail_count.count():
        temps = Temps.get_by_id(temps_id)
        temps.key.delete()

    details_temps.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('frais_tache.index', tache_id=tache_id))