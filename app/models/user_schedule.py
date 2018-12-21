from .. import db
from app.models import Timeoff, Timeoff_Type


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
                    User_schedule.user_id == self.user_id).count()
        return count

    @property
    def used_personal(self):
        count = db.session.query(Timeoff).join(
            User_schedule, Timeoff.schedule).join(
                Timeoff_Type, Timeoff.type).filter(
                    Timeoff_Type.name.in_([
                        'Sick', 'FRL'
                    ])).filter(User_schedule.user_id == self.user_id).count()
        return count

    @property
    def available_vacation(self):
        return (
            self.carriedvacation + self.entitledvacation) - self.used_vacation
