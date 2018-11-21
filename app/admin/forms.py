from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (PasswordField, StringField, SubmitField,
                            IntegerField, BooleanField, TextAreaField,
                            DateField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User, Team, Schedule_year
from datetime import datetime
from math import ceil


def get_remaining_year_ratio(num):
    return int(ceil(num * ((1 / (datetime.now().month / 13) - 1))))


class ChangeAccountTypeForm(Form):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class NewUserScheduleForm(Form):
    year = QuerySelectField(
        'Year',
        validators=[InputRequired()],
        get_label='year',
        query_factory=lambda: db.session.query(Schedule_year).order_by('iscurrent', 'start_date')
    )
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


class ConfirmForm(NewUserScheduleForm):
    startdate = DateField('Start Date')


class NewUserForm(NewUserScheduleForm):
    startdate = DateField('Start Date')
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
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
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
