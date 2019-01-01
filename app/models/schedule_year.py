from .. import db


class Schedule_year(db.Model):
    __tablename__ = 'schedule_years'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    year = db.Column(db.Integer, unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    iscurrent = db.Column(db.Boolean)
    schedules = db.relationship('User_schedule', backref='year')
    pay_periods = db.relationship('Pay_period', backref='year')
    avg_periods = db.relationship('Avg_period', backref='year')
    stats = db.relationship('Stat_day', backref='year')
    import_logs = db.relationship('Import_log', backref='year')
