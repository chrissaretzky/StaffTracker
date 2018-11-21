from .. import db


class Shift(db.Model):
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('user_schedules.id'))
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    isic = db.Column(db.Boolean)
    otbanked = db.Column(db.Boolean)
    otpaid = db.Column(db.Boolean)
    comment = db.Column(db.Text)
