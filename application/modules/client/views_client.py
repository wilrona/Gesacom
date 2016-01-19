__author__ = 'Ronald'

from ...modules import *
from models_client import Client, Contact

from forms_client import FormClient, FormContact

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('client', __name__)
prefix_contact = Blueprint('contact', __name__)


@prefix.route('/')
@prefix.route('/<int:prospect>')
@login_required
@roles_required([('super_admin', 'client')])
def index(prospect=None):
    menu = 'client'
    if prospect:
        submenu = 'prospect'
        title_page = 'Propect'
    else:
        submenu = 'client'
        title_page = 'Client'

    context = 'charge'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if prospect:
        datas = Client.query(Client.prospect == True)
    else:
        datas = Client.query(Client.prospect == False)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Clients')
    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('client/index.html', **locals())


@prefix.route('/edit',  methods=['GET', 'POST'])
@prefix.route('/edit/<int:client_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def edit(client_id=None):
    menu = 'client'

    prospect = request.args.get('prospect')

    if prospect:
        submenu = 'prospect'
        title_page = 'Propect'
    else:
        submenu = 'client'
        title_page = 'Client'

    context = 'information'

    view_accent = False
    if client_id:

        client = Client.get_by_id(client_id)
        form = FormClient(obj=client)
        form.id.data = client_id
        form.ref.data = client.ref

        accent_com = Client.query(
            Client.myself == True
        )
        view_accent = True
        if accent_com.count():
            view_accent = False

    else:
        client = Client()
        form = FormClient()
        success = False

    if form.validate_on_submit():

        client.name = form.name.data
        client.ref = form.ref.data
        client.adresse = form.adresse.data
        client.bp = form.bp.data
        client.email = form.email.data
        client.pays = form.pays.data
        client.ville = form.ville.data
        client.phone = form.phone.data
        if prospect:
            client.prospect = True

        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

        client.date_created = function.datetime_convert(date_auto_nows)
        client.put()

        flash('Enregistrement effectue avec success', 'success')
        success = True


    # if not client_id:
    #     return render_template('client/edit.html', **locals())
    # else:
    return render_template('client/infos.html', **locals())


@prefix.route('/accentcom/<int:client_id>')
@login_required
@roles_required([('super_admin', 'client')])
def accent_com(client_id):
    client = Client.get_by_id(client_id)
    client.myself = True
    client.put()
    return redirect(url_for('client.edit', client_id=client_id))


@prefix.route('/transfert/<int:client_id>')
@login_required
@roles_required([('super_admin', 'client')])
def prospect_client(client_id):
    client = Client.get_by_id(client_id)
    client.prospect = False
    client.put()
    return redirect(url_for('client.edit', client_id=client_id))




@prefix.route('/contact/<int:client_id>', methods=['GET', 'POST'])
@prefix.route('/contact/<int:client_id>/<int:prospect>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client_contact')])
def contact(client_id, prospect=None):
    menu = 'client'
    if prospect:
        submenu = 'prospect'
        title_page = 'Prospect'
    else:
        submenu = 'client'
        title_page = 'Client'
    context = 'contact'

    client = Client.get_by_id(client_id)

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Contact.query(
        Contact.client_id == client.key
    )
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Contact')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('client/contact.html', **locals())


@prefix.route('/contact/edit/<int:client_id>', methods=['GET', 'POST'])
@prefix.route('/contact/edit/<int:client_id>/<int:contact_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client_contact')], ['edit'])
def contact_edit(client_id, contact_id=None):

    user = Client.get_by_id(client_id)

    if contact_id:
        contact = Contact.get_by_id(contact_id)
        form = FormContact(obj=contact)
    else:
        contact = Contact()
        form = FormContact()

    form.client_id.choices = [(0, '')]

    success = False
    if form.validate_on_submit():
        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.email = form.email.data
        contact.phone1 = form.phone1.data
        contact.phone2 = form.phone2.data
        contact.client_id = user.key

        contact.put()
        flash('Enregistrement effectue avec success', 'success')
        success = True

    return render_template('client/contact_edit.html', **locals())


@prefix.route('/contact/delete/<int:client_id>/<int:contact_id>')
@login_required
@roles_required([('super_admin', 'client_contact')], ['delete'])
def contact_delete(client_id, contact_id):

    contact = Contact.get_by_id(contact_id)
    contact.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('client.contact', client_id=client_id))


@prefix.route('/delete/<int:client_id>')
@login_required
@roles_required([('super_admin', 'client')], ['delete'])
def delete(client_id):
    from ..budget.models_budget import ClientBudget
    from ..projet.models_projet import Projet

    prospect = request.args.get('prospect')

    client = Client.get_by_id(client_id)

    projet_client = Projet.query(
        Projet.client_id == client.key
    ).count()

    if projet_client:
        flash('Impossible de supprimer cette element', 'danger')
    else:
        contact_client = Contact.query(
            Contact.client_id == client.key
        )

        budget_client = ClientBudget.query(
            ClientBudget.client_id == client.key
        )

        for contact in contact_client:
            contact.key.delete()

        for client in budget_client:
            client.key.delete()

        client.key.delete()
        flash('Suppression reussie', 'success')

    return redirect(url_for('client.index', prospect=prospect))


@prefix_contact.route('/')
@login_required
@roles_required([('super_admin', 'contact')])
def index():
    menu = 'client'
    submenu = 'contact'
    context = 'charge'
    title_page = 'Client - Contact'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Contact.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Contacts')
    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('client/contacts.html', **locals())


@prefix_contact.route('/edit', methods=['GET', 'POST'])
@prefix_contact.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'contact')], ['edit'])
def contact_edit(contact_id=None):

    client_id = None

    if contact_id:
        contact = Contact.get_by_id(contact_id)
        form = FormContact(obj=contact)
        form.client_id.data = contact.client_id.get().key.id()
    else:
        contact = Contact()
        form = FormContact()

    form.client_id.choices = [(0, 'Selectionnez un client')]
    for choice in Client.query():
        form.client_id.choices.append((choice.key.id(), choice.name))
    form.contact.data = 'contact'

    success = False
    if form.validate_on_submit():

        contact.first_name = form.first_name.data
        contact.last_name = form.last_name.data
        contact.email = form.email.data
        contact.phone1 = form.phone1.data
        contact.phone2 = form.phone2.data

        customer = Client.get_by_id(int(form.client_id.data))

        contact.client_id = customer.key

        contact.put()
        flash('Enregistrement effectue avec success', 'success')
        success = True

    return render_template('client/contact_edit.html', **locals())


@prefix_contact.route('/delete/<int:contact_id>')
def contact_delete(contact_id):
    contact = Contact.get_by_id(contact_id)
    contact.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('contact.index'))