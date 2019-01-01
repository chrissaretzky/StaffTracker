from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (SubmitField, BooleanField, TextAreaField,
                            DateField, DateTimeField, StringField,
                            IntegerField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (InputRequired, Length, Email)

from app import db
from app.models import Role, Team, Timeoff_Type, Schedule_year
from datetime import datetime, timedelta
from math import ceil


def get_remaining_year_ratio(num):
    return int(ceil(num * ((1 / (datetime.now().month / 13) - 1))))


class EditUserScheduleForm(Form):
    carriedvacation = IntegerField('Carried Vacation', default=0)

    entitledvacation = IntegerField(
        'Entitled Vacation', default=get_remaining_year_ratio(15))

    entitledpersonal = IntegerField(
        'Personal Days', default=get_remaining_year_ratio(9))

    isparttime = BooleanField('Part-Time', default=False)
    isaveraging = BooleanField('Averaging Agreement', default=False)

    shiftlength = IntegerField('Shift Length', default=8)

    notes = TextAreaField(label='Notes')

    submit = SubmitField('Submit')


class AddUserScheduleForm(EditUserScheduleForm):
    year = QuerySelectField(
        'Year',
        validators=[InputRequired()],
        get_label='year',
        query_factory=
        lambda: db.session.query(Schedule_year).order_by('iscurrent desc'))


class NewUserScheduleForm(Form):
    team = QuerySelectField(
        'Team',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Team).order_by('name'))

    carriedvacation = IntegerField(
        'Carried Vacation',
        description='Vacation Carried Over From Previous Year',
        default=0)

    entitledvacation = IntegerField(
        'Entitled Vacation',
        description='Vacation For Current Year',
        default=get_remaining_year_ratio(15))

    entitledpersonal = IntegerField(
        'Personal Days',
        description='Entitled Personal Days',
        default=get_remaining_year_ratio(9))

    isparttime = BooleanField('Part-Time', default=False)
    isaveraging = BooleanField('Averaging Agreement', default=False)

    shiftlength = IntegerField(
        'Shift Length',
        default=8,
        description='Length of an employees normal shift in hours')

    notes = TextAreaField(label='Notes')

    submit = SubmitField('Confirm')


class EditUserForm(Form):
    start_date = DateField('Start Date', id='date', format='%m-%d-%Y')
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Update')


class ChangeAccountTypeForm(Form):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class ChangeTeamForm(Form):
    team = QuerySelectField(
        'New Team',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Team))
    submit = SubmitField('Change')


class EditShiftForm(Form):
    startd = DateField(
        'Start Date', validators=[InputRequired()], format='%m-%d-%Y')
    startt = DateTimeField(
        'Start Time', validators=[InputRequired()], format='%I:%M %p')
    endd = DateField(
        'End Date', validators=[InputRequired()], format='%m-%d-%Y')
    endt = DateTimeField(
        'End Time', validators=[InputRequired()], format='%I:%M %p')
    isic = BooleanField('IC')
    training = BooleanField('Training Shift')
    otbanked = BooleanField('Banked OT')
    otpaid = BooleanField('Paid OT')
    comment = TextAreaField('Commments')
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')

    def validate_startd(form, field):
        if form.startd.data > form.endd.data:
            raise ValidationError('End date needs to be after start date')

    def validate_endd(form, field):
        if form.startd.data > form.endd.data:
            raise ValidationError(
                'End time + the End Date needs to be greater than the start...its not'
            )

    def validate_startt(form, field):
        start = datetime.combine(form.startd.data, form.startt.data.time())
        end = datetime.combine(form.endd.data, form.endt.data.time())
        if start > end:
            raise ValidationError(
                'Cmon, start is past end is future, just get it already')

    def validate_endt(form, field):
        start = datetime.combine(form.startd.data, form.startt.data.time())
        end = datetime.combine(form.endd.data, form.endt.data.time())
        if start > end:
            raise ValidationError(
                'The Start time and date needs to be further in the future than the End time and date, its not that hard'
            )

    def validate_otpaid(form, field):
        if form.otbanked.data and form.otpaid.data:
            raise ValidationError(
                'Not able to have both paid and banked selected')


class EditTimeoffForm(Form):
    dayof = DateField('Day', validators=[InputRequired()], format='%m-%d-%Y')
    type_ = QuerySelectField(
        'Type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Timeoff_Type).order_by('name'))
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')


class DeactivateUser(Form):
    term_date = DateField(
        'Termination Date', validators=[InputRequired()], format='%m-%d-%Y')
    submit = SubmitField('Deactivate')
