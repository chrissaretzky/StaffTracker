from .. import db


class Avg_period(db.Model):
    __tablename__ = 'avg_periods'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('schedule_years.id'))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
