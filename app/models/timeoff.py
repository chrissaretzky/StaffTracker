from .. import db


class Timeoff_Type(db.Model):
    __tablename__ = 'timeoff_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    timeoff = db.relationship('Timeoff', backref='type', lazy='dynamic')

    @staticmethod
    def insert_types():
        types = {'Off', 'BDay', 'FRL', 'Sick', 'Vacation', 'Stat'}
        for t in types:
            timeoff_type = Timeoff_Type.query.filter_by(name=t).first()
            if timeoff_type is None:
                timeoff_type = Timeoff_Type(name=t)
                db.session.add(timeoff_type)
        db.session.commit()


class Timeoff(db.Model):
    __tablename__ = 'timeoff'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('user_schedules.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('timeoff_types.id'))
    dayof = db.Column(db.Date, nullable=False)
    partialtime = db.Column(db.Integer)

    @property
    def day(self):
        return self.dayof.strftime("%B-%d")
