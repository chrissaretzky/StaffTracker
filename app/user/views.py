from flask import Blueprint, render_template, url_for, redirect

from app import db
from flask_login import (current_user, login_required)
from app.models import User, Schedule_year, Shift, User_schedule, Timeoff

user = Blueprint('user', __name__)


@user.route('/')
@login_required
def index():
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('user/index.html', user=user)


@user.route('/shift_info')
@login_required
def shift_info():
    user = User.query.filter_by(id=current_user.id).first()
    schedule = db.session.query(User_schedule).join(
        Schedule_year, User_schedule.year).filter(
            Schedule_year.iscurrent).filter(
                User_schedule.user == user).first()
    if schedule is None:
        return redirect(url_for('user.index'))
    else:
        shifts = Shift.query.filter_by(schedule=schedule).all()
        return render_template(
            'user/shift_info.html', user=user, shifts=shifts)


@user.route('/timeoff_info')
@login_required
def timeoff_info():
    user = User.query.filter_by(id=current_user.id).first()
    schedule = User_schedule.query.filter_by(user=user).filter_by(
        active=True).first()
    if schedule is None:
        return redirect(url_for('user.index'))
    else:
        timeoff = Timeoff.query.filter_by(schedule=schedule).all()
        return render_template(
            'user/timeoff_info.html', user=user, timeoff=timeoff)
