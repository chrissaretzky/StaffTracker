from .. import db


class User_schedule(db.Model):
    __tablename__ = 'user_schedules'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    year_id = db.Column(db.Integer, db.ForeignKey('schedule_years.id'))
    active = db.Column(db.Boolean)
    carriedvacation = db.Column(db.Integer)
    entitledvacation = db.Column(db.Integer, nullable=False)
    entitledpersonal = db.Column(db.Integer, nullable=False)
    isparttime = db.Column(db.Boolean, nullable=False)
    isaveraging = db.Column(db.Boolean, nullable=False)
    shiftlength = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    shifts = db.relationship('Shift', backref='schedule')
    timeoff = db.relationship('Timeoff', backref='schedule')
