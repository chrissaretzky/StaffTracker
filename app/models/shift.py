from .. import db


class Shift(db.Model):
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('user_schedules.id'))
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    isic = db.Column(db.Boolean)
    training = db.Column(db.Boolean)
    otbanked = db.Column(db.Boolean)
    otpaid = db.Column(db.Boolean)
    comment = db.Column(db.Text)
    manual_edit = db.Column(db.Boolean, default=False)

    @property
    def day(self):
        return self.start.strftime("%m-%d-%Y")

    @property
    def start_time(self):
        return self.start.strftime("%I:%M%p")

    @property
    def end_time(self):
        return self.end.strftime("%I:%M%p")

    @property
    def hours(self):
        t = self.end - self.start
        return t.total_seconds() / 3600
