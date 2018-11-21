from .. import db


class Timeoff(db.Model):
    __tablename__ = 'timeoff'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('user_schedules.id'))
    dayof = db.Column(db.Date, nullable=False)
    partialtime = db.Column(db.Integer)
    typeof = db.Column(db.String)
