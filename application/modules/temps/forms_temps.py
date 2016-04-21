__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from lib.flaskext.wtf.html5 import NumberInput
from ...modules import *


def control_date(form, field):
    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    send_date = function.date_convert(field.data)

    if not form.derob.data:
        if send_date < function.date_convert(start) or send_date > function.date_convert(end):
            raise wtf.ValidationError('La date doit etre comprise entre '+function.format_date(start, '%d/%m/%Y')+" et "+function.format_date(end, '%d/%m/%Y'))


def control_heure(form, field):

    if not form.derob_day.data and field.data:
        time = str(field.data)
        time = time.split(':')
        if int(time[0]) == 8 and int(time[1]) > 0 and not form.derob_day.data:
            raise wtf.ValidationError('L\'heure est superieure a la periode de travail')

        if int(time[0]) > 8 and not form.derob_day.data:
            raise wtf.ValidationError('L\'heure est superieure a la periode de travail')

        if int(time[0]) == 0 and int(time[1]) == 0 and not form.derob_day.data:
            raise wtf.ValidationError('Impossible de sauvegarder un temps null ou egale a zero')

    if not form.derob_day.data and not field.data:
        raise wtf.ValidationError('Champ Obligatoire')


def control_day(form, field):
    if form.derob_day.data and not field.data:
        raise wtf.ValidationError('Champ Obligatoire et vous devez au moin faire un jour')


class FormTemps(wtf.Form):
    derob = wtf.HiddenField()
    derob_day = wtf.HiddenField()
    date = wtf.DateField(label='Date d\'execution :', format="%d/%m/%Y", validators=[validators.Required('Champ Obligatoire'), control_date])
    description = wtf.TextAreaField(label='Description :', validators=[validators.Required('Champ Obligatoire')])
    heure = wtf.StringField(label='Nbre d\'Heure :', validators=[control_heure], default='00:00')
    jour = wtf.IntegerField(label='Nbre de jour :', default=0, widget=NumberInput(), validators=[control_day])