from .. import db


class User_payroll(db.Model):
    __tablename__ = 'user_payrolls'

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    payroll_id = db.Column(db.Integer, db.ForeignKey('pay_periods.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    issubmitted = db.Column(db.Boolean)
    isverified = db.Column(db.Boolean)
