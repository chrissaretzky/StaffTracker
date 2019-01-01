from flask_wtf import Form
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (PasswordField, StringField, SubmitField, DateField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (Email, EqualTo, InputRequired, Length)

from flask_wtf.file import FileField, FileRequired
from app import db
from app.models import Role, User
from app.admin.manage_user.forms import NewUserScheduleForm


class ConfirmForm(NewUserScheduleForm):
    startdate = DateField('Start Date', format='%m-%d-%Y')


class NewUserForm(NewUserScheduleForm):
    startdate = DateField('Start Date', id='date', format='%m-%d-%Y')
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


class FileUpload(Form):
    upload = FileField('Staffhub Sheet', validators=[FileRequired()])
    submit = SubmitField('Upload')
