from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app import db
from app.account.forms import (ChangePasswordForm, CreatePasswordForm,
                               LoginForm, RegistrationForm)
from app.models import User

account = Blueprint('account', __name__)


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            if user.confirmed:
                if user.active:
                    login_user(user, form.remember_me.data)
                    if user.change_pw:
                        flash('Please change your password', 'warning')
                        return redirect(url_for('account.change_password'))
                    else:
                        if user.role.name == 'Administrator':
                            return redirect(url_for('admin.index'))
                        elif user.role.name == 'User':
                            return redirect(url_for('user.index'))
                        else:
                            abort(404)
                else:
                    flash('Your account is not active', 'error')
            else:
                flash('Waiting for manager to confirm your account', 'warning')
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            confirmed=False,
            username=form.email.data)
        db.session.add(user)
        db.session.commit()
        # token = user.generate_confirmation_token()
        # confirm_link = url_for('account.confirm', token=token, _external=True)
        # send_email(
        #     recipient=user.email,
        #     subject='Confirm Your Account',
        #     template='account/email/confirm',
        #     user=user,
        #     confirm_link=confirm_link)
        flash('Wating for admin to confirm your account', 'warning')
        return redirect(url_for('account.login'))
    return render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


# @account.route('/reset-password', methods=['GET', 'POST'])
# def reset_password_request():
#     """Respond to existing user's request to reset their password."""
#     if not current_user.is_anonymous:
#         return redirect(url_for('main.index'))
#     form = RequestResetPasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user:
#             token = user.generate_password_reset_token()
#             reset_link = url_for(
#                 'account.reset_password', token=token, _external=True)
#             send_email(
#                 recipient=user.email,
#                 subject='Reset Your Password',
#                 template='account/email/reset_password',
#                 user=user,
#                 reset_link=reset_link,
#                 next=request.args.get('next'))
#         return redirect(url_for('account.login'))
#     return render_template('account/reset_password.html', form=form)

# @account.route('/reset-password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     """Reset an existing user's password."""
#     if not current_user.is_anonymous:
#         return redirect(url_for('main.index'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user is None:
#             flash('Invalid email address.', 'form-error')
#             return redirect(url_for('main.index'))
#         if user.reset_password(token, form.new_password.data):
#             flash('Your password has been updated.', 'form-success')
#             return redirect(url_for('account.login'))
#         else:
#             flash('The password reset link is invalid or has expired.',
#                   'form-error')
#             return redirect(url_for('main.index'))
#     return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            current_user.change_pw = False
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.manage'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form)
