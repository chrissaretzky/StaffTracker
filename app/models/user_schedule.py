from .. import db
from app.models import Timeoff, Timeoff_Type, Shift
from sqlalchemy import func
from math import ceil


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

    @property
    def used_vacation(self):
        count = db.session.query(Timeoff).join(
            User_schedule, Timeoff.schedule).join(
                Timeoff_Type,
                Timeoff.type).filter(Timeoff_Type.name == 'Vacation').filter(
                    User_schedule.user_id == self.user_id).filter(User_schedule.year_id == self.year_id).count()
        return count

    @property
    def used_personal(self):
        ratio = 8 / self.shiftlength
        count = db.session.query(Timeoff).join(
            User_schedule, Timeoff.schedule).join(
                Timeoff_Type, Timeoff.type).filter(
                    Timeoff_Type.name.in_([
                        'Sick', 'FRL'
                    ])).filter(User_schedule.user_id == self.user_id).filter(User_schedule.year_id == self.year_id).count()
        return ceil(count * ratio)

    @property
    def banked_ot(self):
        recs = db.session.query(Shift). \
            join(User_schedule, Shift.schedule). \
            filter(Shift.otbanked). \
            filter(User_schedule.user_id == self.user_id). \
            filter(User_schedule.year_id == self.year_id). \
            all()
        
        s = 0
        for rec in recs:
            s = s + rec.hours

        return int(ceil((s*2)/self.shiftlength))

    @property
    def available_vacation(self):
        ratio = 8 / self.shiftlength
        return ceil(((self.carriedvacation + self.entitledvacation + self.banked_ot) - self.used_vacation)*ratio)
