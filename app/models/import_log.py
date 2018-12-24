from .. import db
import datetime


class Import_log(db.Model):
    __tablename__ = 'import_logs'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('schedule_years.id'))
    run_date = db.Column(db.DateTime, default=datetime.datetime.now())
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    schema_errors = db.Column(db.PickleType)
    invalid_colors = db.Column(db.PickleType)
    invalid_times = db.Column(db.PickleType)
    invalid_header = db.Column(db.PickleType)
    records = db.Column(db.Integer)
    dates = db.Column(db.PickleType)
    employees = db.Column(db.PickleType)
    _type = db.Column(db.String(64))
