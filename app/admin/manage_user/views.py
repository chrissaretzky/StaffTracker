from flask import (Blueprint, abort, flash, redirect, render_template, url_for)
from flask_login import current_user, login_required

from app import db
from app.admin.manage_user.forms import (
    ChangeAccountTypeForm, ChangeTeamForm, EditUserForm, EditShiftForm,
    EditTimeoffForm, EditUserScheduleForm, AddUserScheduleForm)
from app.decorators import admin_required
from app.models import (User, User_schedule, Shift, Schedule_year, Timeoff)
from datetime import datetime

manage_user = Blueprint('manage_user', __name__)


@manage_user.route('/<int:user_id>')
@manage_user.route('/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    schedules = User_schedule.query.filter_by(user=user).all()
    #schedules.sort(key=lambda x: print(x.year.iscurrent), reverse=True)
    if user is None:
        abort(404)
    if user.confirmed is False:
        return redirect(url_for('admin.confirm_user', user_id=user_id))
    return render_template(
        'admin/manage_user/user_info.html', user=user, schedules=schedules)


@manage_user.route('/<int:user_id>/edit_user', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    if user.confirmed is False:
        return redirect(url_for('admin.confirm_user', user_id=user_id))
    form = EditUserForm(
        start_date=user.start_date,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email)
    if form.validate_on_submit():
        user.start_date = form.start_date.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        if user.email == form.email.data:
            user.email = form.email.data
        else:
            email_check = User.query.filter_by(email=form.email.data).first()
            if not email_check:
                user.email = form.email.data
        db.session.commit()
        return redirect(url_for('manage_user.user_info', user_id=user_id))

    return render_template(
        'admin/manage_user/user_info.html', user=user, form=form)


@manage_user.route(
    '/<int:user_id>/edit_schedule/<int:sched_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_schedule(user_id, sched_id):
    user = User.query.filter_by(id=user_id).first()
    schedule = User_schedule.query.filter_by(user=user).filter_by(
        id=sched_id).first()
    if schedule:
        form = EditUserScheduleForm(
            carriedvacation=schedule.carriedvacation,
            entitledvacation=schedule.entitledvacation,
            entitledpersonal=schedule.entitledpersonal,
            isparttime=schedule.isparttime,
            isaveraging=schedule.isaveraging,
            shiftlength=schedule.shiftlength,
            notes=schedule.notes)
        if form.validate_on_submit():
            schedule.carriedvacation = form.carriedvacation.data
            schedule.entitledvacation = form.entitledvacation.data
            schedule.entitledpersonal = form.entitledpersonal.data
            schedule.isparttime = form.isparttime.data
            schedule.isaveraging = form.isaveraging.data
            schedule.shiftlength = form.shiftlength.data
            schedule.notes = form.notes.data
            db.session.commit()
            flash('Schedule updated', 'positive')
            return redirect(url_for('manage_user.user_info', user_id=user_id))
        else:
            return render_template(
                'admin/manage_user/user_info.html', user=user, form=form)
    else:
        flash('Selected schedule does not belong to the user you hacker',
              'error')
        return redirect(url_for('manage_user.user_info', user_id=user_id))


@manage_user.route('/<int:user_id>/add_schedule', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = AddUserScheduleForm()
    if form.validate_on_submit():
        schedule = User_schedule()
        schedule.user = user
        schedule.year = form.year.data
        schedule.carriedvacation = form.carriedvacation.data
        schedule.entitledvacation = form.entitledvacation.data
        schedule.entitledpersonal = form.entitledpersonal.data
        schedule.isparttime = form.isparttime.data
        schedule.isaveraging = form.isaveraging.data
        schedule.shiftlength = form.shiftlength.data
        schedule.notes = form.notes.data
        db.session.commit()
        flash('Schedule updated', 'positive')
        return redirect(url_for('manage_user.user_info', user_id=user_id))
    else:
        return render_template(
            'admin/manage_user/user_info.html', user=user, form=form)
    return redirect(url_for('manage_user.user_info', user_id=user_id))


@manage_user.route('/<int:user_id>/shift_info')
@login_required
@admin_required
def shift_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    schedule = db.session.query(User_schedule).join(
        Schedule_year, User_schedule.year).filter(
            Schedule_year.iscurrent).filter(
                User_schedule.user == user).first()
    if schedule is None:
        flash('User does not have an active schedule', 'error')
        return redirect(url_for('manage_user.user_info', user_id=user_id))
    else:
        shifts = Shift.query.filter_by(schedule=schedule).all()
        return render_template(
            'admin/manage_user/shift_info.html', user=user, shifts=shifts)


@manage_user.route(
    '/<int:user_id>/edit_shift/<int:shift_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_shift(user_id, shift_id):
    user = User.query.filter_by(id=user_id).first()
    shift = Shift.query.filter_by(id=shift_id).first()
    if shift:
        form = EditShiftForm(
            startd=shift.start.date(),
            startt=shift.start.time(),
            endd=shift.end.date(),
            endt=shift.end.time(),
            isic=shift.isic,
            training=shift.training,
            otbanked=shift.otbanked,
            otpaid=shift.otpaid,
            comment=shift.comment)
        if form.validate_on_submit():
            if form.delete.data:
                db.session.delete(shift)
                db.session.commit()
                flash('Deleted shift', 'positive')
                return redirect(
                    url_for('manage_user.shift_info', user_id=user_id))
            else:
                shift.start = datetime.combine(form.startd.data,
                                               form.startt.data.time())
                shift.end = datetime.combine(form.endd.data,
                                             form.endt.data.time())
                shift.isic = form.isic.data
                shift.training = form.training.data
                shift.otbanked = form.otbanked.data
                shift.otpaid = form.otpaid.data
                shift.comment = form.comment.data
                shift.manual_edit = True
                db.session.commit()
                flash('Changed shift', 'positive')
                return redirect(
                    url_for('manage_user.shift_info', user_id=user_id))
        return render_template(
            'admin/manage_user/shift_info.html',
            user=user,
            form=form,
            shift=shift)
    else:
        return redirect(url_for('manage_user.user_info', user_id=user_id))


@manage_user.route('/<int:user_id>/new_shift', methods=['GET', 'POST'])
@login_required
@admin_required
def new_shift(user_id):
    user = User.query.filter_by(id=user_id).first()
    year = Schedule_year.query.filter_by(iscurrent=True).first()
    schedule = User_schedule.query.filter_by(year=year).filter_by(
        user=user).first()
    if schedule:
        form = EditShiftForm()
        if form.validate_on_submit():
            shift = Shift()
            shift.schedule = schedule
            shift.start = datetime.combine(form.startd.data,
                                           form.startt.data.time())
            shift.end = datetime.combine(form.endd.data, form.endt.data.time())
            shift.isic = form.isic.data
            shift.training = form.training.data
            shift.otbanked = form.otbanked.data
            shift.otpaid = form.otpaid.data
            shift.comment = form.comment.data
            shift.manual_edit = True
            db.session.add(shift)
            db.session.commit()
            flash('Added Shift', 'positive')
            return redirect(url_for('manage_user.shift_info', user_id=user_id))
    return render_template(
        'admin/manage_user/shift_info.html', user=user, form=form)


@manage_user.route('/<int:user_id>/timeoff_info')
@login_required
@admin_required
def timeoff_info(user_id):
    user = User.query.filter_by(id=user_id).first()
    schedule = User_schedule.query.filter_by(user=user).filter_by(
        active=True).first()
    if schedule is None:
        flash('User does not have an active schedule', 'error')
        return redirect(url_for('manage_user.user_info', user_id=user_id))
    else:
        timeoff = Timeoff.query.filter_by(schedule=schedule).all()
        return render_template(
            'admin/manage_user/timeoff_info.html', user=user, timeoff=timeoff)


@manage_user.route(
    '/<int:user_id>/edit_timeoff/<int:timeoff_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_timeoff(user_id, timeoff_id):
    user = User.query.filter_by(id=user_id).first()
    timeoff = Timeoff.query.filter_by(id=timeoff_id).first()
    if timeoff:
        form = EditTimeoffForm(dayof=timeoff.dayof, type_=timeoff.type)
        if form.validate_on_submit():
            if form.delete.data:
                db.session.delete(timeoff)
                db.session.commit()
                flash('Deleted shift', 'positive')
                return redirect(
                    url_for('manage_user.timeoff_info', user_id=user_id))
            else:
                timeoff.dayof = form.dayof.data
                timeoff.type = form.type_.data
                db.session.commit()
                flash('Changed timeoff', 'positive')
                return redirect(
                    url_for('manage_user.timeoff_info', user_id=user_id))
        return render_template(
            'admin/manage_user/timeoff_info.html',
            user=user,
            form=form,
            timeoff=timeoff)
    else:
        return redirect(url_for('manage_user.user_info', user_id=user_id))


@manage_user.route('/<int:user_id>/new_timeoff', methods=['GET', 'POST'])
@login_required
@admin_required
def new_timeoff(user_id):
    user = User.query.filter_by(id=user_id).first()
    year = Schedule_year.query.filter_by(iscurrent=True).first()
    schedule = User_schedule.query.filter_by(year=year).filter_by(
        user=user).first()
    if schedule:
        form = EditTimeoffForm()
        if form.validate_on_submit():
            timeoff = Timeoff()
            timeoff.dayof = form.dayof.data
            timeoff.type = form.type_.data
            timeoff.schedule = schedule
            db.session.add(timeoff)
            db.session.commit()
            flash('Added Schedule', 'positive')
            return redirect(
                url_for('manage_user.timeoff_info', user_id=user_id))
    return render_template(
        'admin/manage_user/timeoff_info.html', user=user, form=form)


@manage_user.route(
    '/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash(
            'You cannot change the type of your own account. Please ask '
            'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash(
            'Role for user {} successfully changed to {}.'.format(
                user.full_name(), user.role.name), 'form-success')
    return render_template(
        'admin/manage_user/user_info.html', user=user, form=form)


@manage_user.route('/<int:user_id>/change_team', methods=['GET', 'POST'])
@login_required
@admin_required
def change_team(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeTeamForm()
    if form.validate_on_submit():
        user.team = form.team.data
        db.session.commit()
        flash(
            'Team for user {} successfully changed to {}.'.format(
                user.full_name(), user.team.name), 'form-success')
    return render_template(
        'admin/manage_user/user_info.html', user=user, form=form)


@manage_user.route('/<int:user_id>/deactivate')
@login_required
@admin_required
def deactivate_user(user_id):
    if current_user.id == user_id:
        flash(
            'You cannot dactivate yourself dumbass. Please ask another '
            'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404)
        user.active = False
        db.session.commit()
        flash('Deactivate user %s.' % user.full_name(), 'success')
    return redirect(url_for('manage_user.user_info', user_id=user.id))


@manage_user.route('/<int:user_id>/reactivate')
@login_required
@admin_required
def reactivate_user(user_id):
    if current_user.id == user_id:
        flash(
            'You cannot reactivate yourself dumbass. Please ask another '
            'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404)
        user.active = True
        db.session.commit()
        flash('reactivated user %s.' % user.full_name(), 'success')
    return redirect(url_for('manage_user.user_info', user_id=user.id))
