__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
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
    time = str(field.data)
    time = time.split(':')
    if int(time[0]) == 8 and int(time[1]) > 0:
        raise wtf.ValidationError('L\'heure est superieure a la periode de travail')

    if int(time[0]) > 8:
        raise wtf.ValidationError('L\'heure est superieure a la periode de travail')

    if int(time[0]) == 0 and int(time[1]) == 0:
        raise wtf.ValidationError('Impossible de sauvegarder un temps null ou egale a zero')


class FormTemps(wtf.Form):
    derob = wtf.HiddenField()
    date = wtf.DateField(label='Date de debut :', format="%d/%m/%Y", validators=[validators.Required('Champ Obligatoire'), control_date])
    description = wtf.TextAreaField(label='Description :', validators=[validators.Required('Champ Obligatoire')])
    heure = wtf.StringField(label='Nbre d\'Heure :', validators=[validators.Required('Champ Obligatoire'), control_heure])