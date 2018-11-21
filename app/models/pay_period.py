from .. import db


class Pay_period(db.Model):
    __tablename__ = 'pay_periods'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('schedule_years.id'))
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    payrolls = db.relationship('User_payroll', backref='period')
