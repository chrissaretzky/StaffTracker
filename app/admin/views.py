from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for, jsonify)
from flask_login import current_user, login_required

from app import db
from app.admin.forms import (NewUserForm, ConfirmForm, FileUpload)
from app.decorators import admin_required
from app.models import (EditableHTML, Role, User, User_schedule, Shift,
                        Schedule_year, Timeoff, Team, Timeoff_Type, Import_log)
from app.admin.utils.staffhub_import import Shifts_Import, TimeOff_Import
from datetime import timedelta, datetime
import subprocess

admin = Blueprint('admin', __name__)


def backup_db():
    subprocess.call(
        'C:\\Users\\csaretzky\\staff_tracker\\StaffTracker\\backup\\backup.bat'
    )


def import_schedule_data(file, year):
    shift_imp = Shifts_Import(file, year)
    if not shift_imp.isValidated:
        return shift_imp.log
    else:
        backup_db()
        rec_range = [
            shift_imp.valid_data[0]['shiftstart'],
            shift_imp.valid_data[len(shift_imp.valid_data) - 1]['shiftend']
        ]
        db.session.query(Shift).filter(Shift.start >= rec_range[0]).filter(
            Shift.end <= rec_range[1]).filter(
                Shift.manual_edit == False).delete()
        db.session.commit()

        for d in shift_imp.valid_data:
            user = User.query.filter_by(first_name=d['first_name']).filter_by(
                last_name=d['last_name']).first()
            if user:
                schedule_year = Schedule_year.query.filter_by(
                    year=year).first()
                user_schedule = User_schedule.query.filter_by(
                    user=user, year=schedule_year).first()
                if user_schedule:
                    shift = Shift(
                        schedule=user_schedule,
                        start=d['shiftstart'],
                        end=d['shiftend'],
                        isic=d['isic'],
                        training=d['training'],
                        otbanked=d['otbanked'],
                        otpaid=d['otpaidout'],
                        comment=d['comment'])
                    db.session.add(shift)

        timeoff_imp = TimeOff_Import(file, year)
        rec_range = [
            timeoff_imp.valid_data[0]['dayof'],
            timeoff_imp.valid_data[len(timeoff_imp.valid_data) - 1]['dayof']
        ]

        db.session.query(Timeoff).filter(Timeoff.dayof >= rec_range[0]).filter(
            Timeoff.dayof <= rec_range[1]).delete()
        db.session.commit()

        for d in timeoff_imp.valid_data:
            user = User.query.filter_by(first_name=d['first_name']).filter_by(
                last_name=d['last_name']).first()
            if user:
                schedule_year = Schedule_year.query.filter_by(
                    year=year).first()
                user_schedule = User_schedule.query.filter_by(
                    user=user, year=schedule_year).first()
                if user_schedule:
                    timeoff = Timeoff(
                        schedule=user_schedule,
                        dayof=d['dayof'],
                        partialtime=d['partialtime'],
                        type=Timeoff_Type.query.filter_by(
                            name=d['type']).first())
                    db.session.add(timeoff)
        log = Import_log(
            run_date=datetime.now(),
            start=rec_range[0],
            end=rec_range[1],
            schema_errors=shift_imp.log['schema_errors'],
            invalid_colors=shift_imp.log['invalid_colors'],
            invalid_times=shift_imp.log['invalid_times'],
            invalid_header=shift_imp.log['invalid_header'],
            records=shift_imp.log['records'],
            dates=shift_imp.log['dates'],
            employees=shift_imp.log['employees'],
            _type=shift_imp.log['type'])
        db.session.add(log)
        db.session.commit()
        return None


@admin.route('/')
@login_required
@admin_required
def index():
    cnt_unconf_users = User.query.filter_by(confirmed=False).filter_by(
        active=True).count()
    return render_template(
        'admin/index.html', cnt_unconf_users=cnt_unconf_users)


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm(team=Team.query.filter_by(name='SC').first())
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            team=form.team.data,
            confirmed=True,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            username=form.email.data,
            start_date=form.startdate.data,
            change_pw=True)
        user_schedule = User_schedule(
            user=user,
            year=Schedule_year.query.filter_by(iscurrent=True).first(),
            active=True,
            carriedvacation=form.carriedvacation.data,
            entitledvacation=form.entitledvacation.data,
            entitledpersonal=form.entitledpersonal.data,
            isparttime=form.isparttime.data,
            isaveraging=form.isaveraging.data,
            shiftlength=form.shiftlength.data,
            notes=form.notes.data)
        db.session.add(user)
        db.session.add(user_schedule)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.filter_by(confirmed=True).all()
    roles = Role.query.all()
    teams = Team.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles, teams=teams)



@admin.route('/shift_info', methods=['GET', 'POST'])
@login_required
@admin_required
def shift_info():
    roles = Role.query.all()
    teams = Team.query.all()
    years = Schedule_year.query.order_by(Schedule_year.iscurrent.desc()).all()

    if request.method == 'POST':
        year_id = request.form['year']
    else:
        year_id = Schedule_year.query.filter_by(iscurrent=True).first().id
    year_id = 1

    shift_qry = db.session.query(Shift). \
                join(User_schedule). \
                join(User). \
                join(Team). \
                join(Role). \
                join(Schedule_year). \
                filter(Schedule_year.id == year_id)

    shift_low = shift_qry.order_by(Shift.start.asc()).first()
    shift_high = shift_qry.order_by(Shift.end.desc()).first()
    weeks = get_weeks(shift_low.start, shift_high.end)
    week_stats = []
    for w in weeks:
        w_stats = {
            'week':w[0].strftime('%x'),
            'SC_R':0,
            'SC_IC':0,
            'SC_OTB':0,
            'SC_OTP':0,
            'SC_T':0,
            'SC_ADMIN': 0,
            'CS_R':0,
            'CS_ADMIN':0,
            'ES_R':0,
            'ES_ADMIN':0,
            'ATS_R':0,
            'ATS_ADMIN':0
        }
        qry = shift_qry.filter(Shift.start >= w[0]).filter(Shift.end <= w[1]).all()
        for r in qry:
            if r.schedule.user.team.name == 'SC':
                if r.schedule.user.role.name == 'Administrator':
                    w_stats['SC_ADMIN'] += r.hours
                if r.isic:
                    w_stats['SC_IC'] += r.hours
                if r.otbanked:
                    w_stats['SC_OTB'] += r.hours
                if r.otpaid:
                    w_stats['SC_OTP'] += r.hours
                if r.training:
                    w_stats['SC_T'] += r.hours
                w_stats['SC_R'] += r.hours
            if r.schedule.user.team.name == 'CS':
                if r.schedule.user.role.name == 'Administrator':
                    w_stats['CS_ADMIN'] += r.hours
                w_stats['CS_R'] += r.hours
            if r.schedule.user.team.name == 'ES':
                if r.schedule.user.role.name == 'Administrator':
                    w_stats['ES_ADMIN'] += r.hours
                w_stats['ES_R'] += r.hours
            if r.schedule.user.team.name == 'ATS':
                if r.schedule.user.role.name == 'Administrator':
                    w_stats['ATS_ADMIN'] += r.hours
                w_stats['ATS_R'] += r.hours
            
        week_stats.append(w_stats)
    return render_template(
        'admin/shift_info.html', week_stats=week_stats, roles=roles, teams=teams, years=years)

def get_weeks(start, end):
    weeks = []
    if start.isoweekday() == 7:
        week_e = start + timedelta(6)
        weeks.append((start, week_e))
    else:
        week_e = start + timedelta(6 - start.isoweekday())
        weeks.append((start, start + timedelta(6)))
    
    d_iter = week_e + timedelta(1)
    while(d_iter < end):
        week_e = d_iter + timedelta(6)
        weeks.append((d_iter, week_e))
        d_iter = week_e + timedelta(1)
    return weeks
        


@admin.route('/timeoff_info')
@login_required
@admin_required
def timeoff_info():
    timeoff = db.session.query(Timeoff).join(User_schedule).join(
        Schedule_year).filter(Schedule_year.iscurrent == True).all()
    return render_template('admin/timeoff_info.html', timeoff=timeoff)


@admin.route('/unconfirmed_users')
@login_required
@admin_required
def unconfirmed_users():
    """View all registered users."""
    users = User.query.filter_by(confirmed=False).all()
    if len(users) == 0:
        flash('No unconfirmed users', 'warning')
        return redirect(url_for('admin.index'))
    return render_template('admin/unconfirmed_users.html', users=users)


@admin.route('/user/<int:user_id>/confirm', methods=['GET', 'POST'])
@login_required
@admin_required
def confirm_user(user_id):
    form = ConfirmForm()
    user = User.query.filter_by(id=user_id).first()
    year = Schedule_year.query.filter_by(iscurrent=True).first()
    if user is None:
        abort(404)
    if form.validate_on_submit():
        user_schedule = User_schedule(
            user=user,
            year=year,
            carriedvacation=form.carriedvacation.data,
            entitledvacation=form.entitledvacation.data,
            entitledpersonal=form.entitledpersonal.data,
            isparttime=form.isparttime.data,
            isaveraging=form.isaveraging.data,
            shiftlength=form.shiftlength.data,
            notes=form.notes.data)
        user.confirmed = True
        user.team = form.team.data
        user.start_date = form.startdate.data
        db.session.add(user_schedule)
        db.session.commit()
        return redirect(url_for('manage_user.user_info', user_id=user_id))
    if user.confirmed is True:
        return redirect(url_for('manage_user.user_info', user_id=user_id))
    return render_template(
        'admin/confirm_user.html', form=form, user_id=user_id)


@admin.route('/user/<int:user_id>/_delete/<string:return_direction>')
@login_required
@admin_required
def delete_user(user_id, return_direction):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash(
            'You cannot delete your own account. Please ask another '
            'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for(return_direction))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/data_import')
@login_required
@admin_required
def data_import():
    return render_template('admin/data_imports.html')


@admin.route('/data_import/staffhub_import', methods=['GET', 'POST'])
@login_required
@admin_required
def staffhub_import():
    error = None
    year = Schedule_year.query.filter_by(iscurrent=True).first()
    last_shift = Shift.query.order_by(Shift.end.desc()).first()
    form = FileUpload()
    if form.validate_on_submit():
        if year:
            error = import_schedule_data(form.upload.data, year.year)
            if error:
                error = error
    logs = Import_log.query.order_by(Import_log.run_date.desc()).all()
    return render_template(
        'admin/data_imports.html',
        form=form,
        year=year,
        last_shift=last_shift,
        logs=logs,
        error=error)


@admin.route('/schedule_maintenance')
@admin.route('/schedule_maintenance/<int:year_id>')
@admin.route('/schedule_maintenance/<int:year_id>/<int:iscurrent>')
@login_required
@admin_required
def schedule_maintenance(year_id=None, iscurrent=0):
    years = Schedule_year.query.order_by(Schedule_year.year.desc()).all()

    if iscurrent == 1:
        Schedule_year.query.filter_by(iscurrent=True).first().iscurrent = False
        active_year = Schedule_year.query.filter_by(id=year_id).first()
        active_year.iscurrent = True
    elif year_id:
        active_year = Schedule_year.query.filter_by(id=year_id).first()
    else:
        active_year = Schedule_year.query.filter_by(iscurrent=True).first()

    # if active_year:
    #     sql = text('''  SELECT u.id, u.first_name, u.last_name, t.name FROM user_schedules us
    #                     INNER JOIN schedule_years sy ON sy.id = year_id
    #                     FULL JOIN users u ON u.id = us.user_id
    #                     INNER JOIN teams t ON u.team_id = t.id
    #                     WHERE us.id IS NULL
    #                     OR us.year_id <> {}
    #                     AND (SELECT id FROM user_schedules WHERE id = {}) is null'''.format(int(active_year.id), int(active_year.id)))
    #     schedules = db.engine.execute(sql)

    return render_template(
        'admin/schedule_maintenance.html', year=active_year, years=years)
