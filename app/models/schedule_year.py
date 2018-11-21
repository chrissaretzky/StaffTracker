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

    def create_first_year():
        year = Schedule_year()
        year.year = '2018'
        year.start_date = '2017-12-31'
        year.end_date = '2018-12-31'
        year.iscurrent = True
        db.session.add(year)
        db.session.commit()
