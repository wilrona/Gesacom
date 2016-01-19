__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import DetailTemps
from ..tache.models_tache import Tache
from ..budget.models_budget import Budget, BudgetPrestation, Prestation, Client

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('stat', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'stat')])
def index():
    menu = 'stat'
    submenu = ''
    context = 'list'
    title_page = 'Statistique et rapport'

    return render_template('rapport/index.html', **locals())


@prefix.route('/collaborateur')
@login_required
@roles_required([('super_admin', 'stat')])
def collaborateur():
    menu = 'stat'
    submenu = 'collaborateur'
    title_page = 'Remplissage des feuilles de temps par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)


    analyse = []
    for detail in temps_year:
        infos = {}
        infos['user'] = detail.temps_id.get().user_id
        infos['user_infos'] = 1
        infos['tache'] = detail.temps_id.get().tache_id.get().key.id()
        infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
        if detail.temps_id.get().tache_id.get().facturable:
            infos['facturable'] = 1
        else:
            infos['facturable'] = 0

        infos['time'] = detail.conversion
        analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []
    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))
        temp_dict['dev_time'] = 0
        temp_dict['form_time'] = 0
        temp_dict['prod_time_fact'] = 0
        temp_dict['prod_time_nfact'] = 0
        temp_dict['adm_time'] = 0
        temp_dict['total'] = 0

        dev_tot = 0
        adm_tot = 0
        prod_tot_fact = 0
        prod_tot_nfact = 0
        form_tot = 0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']
            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']
            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] = item['time']
                adm_tot += item['time']
            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']
            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']

        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot
        total += temp_dict['total']

        analyses.append(temp_dict)

    return render_template('rapport/collaborateur.html', **locals())


@prefix.route('/taux-chargeabilite-heure-production')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HProd():
    menu = 'stat'
    submenu = 'taux_HProd'
    title_page = 'Taux de chargeabilite des heures de production'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = detail.conversion
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HP_charge = 0
    total_HP_fact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        prest_prod = Prestation.query(
            Prestation.sigle == 'PRO'
        ).get()

        budget_prod = BudgetPrestation.query(
            BudgetPrestation.budget_id == budget.key,
            BudgetPrestation.prestation_id == prest_prod.key
        ).get()

        temp_dict['budget'] = budget_prod.heure
        temp_dict['HProd_Charg'] = 0
        temp_dict['HProd_Fact'] = 0

        HProd_Charg = 0
        HProd_Fact = 0

        for item in grp:
            temp_dict['HProd_Charg'] += item['time']
            HProd_Charg += item['time']
            if item['facturable'] and item['end']:
                temp_dict['HProd_Fact'] += item['time']
                HProd_Fact += item['time']

        temp_dict['Pourc_Charg'] = (temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg']
        temp_dict['Pourc_Bubget'] = (temp_dict['HProd_Fact'] * 100) / temp_dict['budget']
        temp_dict['ecart'] = temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']


        total_bud += temp_dict['budget']
        total_HP_charge += HProd_Charg
        total_HP_fact += HProd_Fact
        total_pourc_c += temp_dict['Pourc_Charg']
        total__budget += temp_dict['Pourc_Bubget']

        analyses.append(temp_dict)

    return render_template('rapport/taux_heure_production.html', **locals())


@prefix.route('/taux-chargeabilite-heure-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HDispo():
    menu = 'stat'
    submenu = 'taux_HDispo'
    title_page = 'Taux de chargeabilite des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        infos = {}
        infos['user'] = detail.temps_id.get().user_id
        infos['user_infos'] = 1
        if detail.temps_id.get().tache_id.get().facturable:
            infos['facturable'] = 1
        else:
            infos['facturable'] = 0
        infos['time'] = detail.conversion
        infos['end'] = detail.temps_id.get().tache_id.get().end
        analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HDispo = 0
    total_HFact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        temp_dict['budget'] = budget.heure
        temp_dict['HDispo'] = 0
        temp_dict['HFact'] = 0

        HDispo = 0
        HFact = 0

        for item in grp:
            temp_dict['HDispo'] += item['time']
            HDispo += item['time']
            if item['facturable'] and item['end']:
                temp_dict['HFact'] += item['time']
                HFact += item['time']

        temp_dict['Pourc_HD'] = (temp_dict['HFact'] * 100) / temp_dict['HDispo']
        temp_dict['Pourc_Bubget'] = (temp_dict['HFact'] * 100) / temp_dict['budget']
        temp_dict['ecart'] = temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']


        total_bud += temp_dict['budget']
        total_HDispo += HDispo
        total_HFact += HFact
        total_pourc_c += temp_dict['Pourc_HD']
        total__budget += temp_dict['Pourc_Bubget']

        analyses.append(temp_dict)

    return render_template('rapport/taux_heure_disponible.html', **locals())


@prefix.route('/etat-consommation-heures-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso():
    menu = 'stat'
    submenu = 'etat_conso'
    title_page = 'Etat de consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        infos = {}
        infos['user'] = detail.temps_id.get().user_id
        infos['user_infos'] = 1
        infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
        infos['time'] = detail.conversion
        analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0
    total_adm = 0
    total_form = 0
    total_dev = 0
    total_prod = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        temp_dict['budget'] = budget.heure
        temp_dict['dev_time'] = 0
        temp_dict['form_time'] = 0
        temp_dict['prod_time'] = 0
        temp_dict['adm_time'] = 0

        dev_tot = 0
        adm_tot = 0
        prod_tot = 0
        form_tot = 0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']
            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']
            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']
            if item['prestation'] == 'PRO':
                temp_dict['prod_time'] += item['time']
                prod_tot += item['time']

        total_budget += temp_dict['budget']
        total_adm += adm_tot
        total_form += form_tot
        total_dev += dev_tot
        total_prod += prod_tot

        analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_disponible.html', **locals())


@prefix.route('/etat-consommation-heure-production')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso_prod():
    menu = 'stat'
    submenu = 'etat_conso_prod'
    title_page = 'Consommation des heures productions'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['time'] = detail.conversion
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0
    total_conso_prod = 0
    total_solde = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        prest_prod = Prestation.query(
            Prestation.sigle == 'PRO'
        ).get()

        budget_prod = BudgetPrestation.query(
            BudgetPrestation.budget_id == budget.key,
            BudgetPrestation.prestation_id == prest_prod.key
        ).get()

        temp_dict['budget'] = budget_prod.heure
        temp_dict['conso_prod'] = 0


        for item in grp:
            temp_dict['conso_prod'] += item['time']

        total_budget += temp_dict['budget']
        temp_dict['solde'] = temp_dict['budget'] - temp_dict['conso_prod']
        total_conso_prod += temp_dict['conso_prod']
        total_solde += temp_dict['solde']

        analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_production.html', **locals())


@prefix.route('/heure-de-developpement-chargee')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_dev_charge():
    menu = 'stat'
    submenu = 'etat_conso_prod'
    title_page = 'Heures de developpement chargees'

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    temps_year = DetailTemps.query()
    for bud in temps_year:
        year = {}
        year['date'] = bud.date.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            if key not in list_year:
                list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'DEV':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            if detail.temps_id.get().tache_id.get().projet_id:
                infos['client'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id
                infos['prospect'] = detail.temps_id.get().tache_id.get().projet_id.get().prospect_id
            else:
                client_accent = Client.query(
                    Client.myself == True
                ).get()
                infos['client'] = client_accent
                infos['prospect'] = None

            infos['user_infos'] = 1
            infos['time'] = detail.conversion
            analyse.append(infos)

    return render_template('rapport/heure-de-developpement-chargee.html', **locals())