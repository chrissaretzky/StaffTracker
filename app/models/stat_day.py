from .. import db


class Stat_day(db.Model):
    __tablename__ = 'stat_days'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('schedule_years.id'))
    dayof = db.Column(db.Date, nullable=False)
    holiday = db.Column(db.String)
