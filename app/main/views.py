from flask import Blueprint, render_template, url_for, redirect

from app.models import EditableHTML

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('account.login'))
