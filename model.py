from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


db = SQLAlchemy(metadata=metadata)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    emp_number = db.Column(db.Integer, db.ForeignKey("employee.emp_number"))
    employee = db.relationship("Employee", backref=db.backref("user", uselist=False))
    is_admin = db.Column(db.Boolean)
    reset_password_page = db.Column(db.Boolean)
    office_code = db.Column(db.Integer)
    is_approver = db.Column(db.Boolean)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    def is_authenticated(self):
        return True


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_code = db.Column(db.Integer)

    customer = db.Column(db.String, nullable=False)
    date = db.Column(db.Date)
    amount = db.Column(db.Integer)

    mode = db.Column(db.String)
    modeentry = db.Column(db.String)
    customerid = db.Column(db.String)

    rel_manager = db.Column(db.String)
    broker = db.Column(db.String)
    nature = db.Column(db.String)

    remarks = db.Column(db.String)
    underwriter = db.Column(db.String)
    ticket = db.Column(db.String)

    status = db.Column(db.String)
    voucher = db.Column(db.String)
    created = db.Column(db.DateTime)

    history = db.Column(db.Text)
    completed = db.Column(db.DateTime)
    proposal = db.Column(db.String)

    policyno = db.Column(db.String)
    instrumentno = db.Column(db.String)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_code = db.Column(db.Integer)
    emp_number = db.Column(db.Integer, unique=True)  # , primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    leave_as_on = db.Column(db.Date)
    count_casual_leave = db.Column(db.Integer)
    count_earned_leave = db.Column(db.Integer)
    count_sick_leave = db.Column(db.Integer)
    count_restricted_holiday = db.Column(db.Integer)
    history_casual_leave = db.Column(db.Text)
    history_earned_leave = db.Column(db.Text)
    history_sick_leave = db.Column(db.Text)
    history_special_leave = db.Column(db.Text)
    history_leave_encashment = db.Column(db.Text)
    history_restricted_holiday = db.Column(db.Text)
    lapsed_sick_leave = db.Column(db.Integer)
    lapsed_earned_leave = db.Column(db.Integer)


class Leaves(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    emp_number = db.Column(db.Integer, db.ForeignKey("employee.emp_number"))
    employee = db.relationship(
        "Employee", backref=db.backref("employee")  # , uselist=False)
    )
    date_of_leave = db.Column(db.Date)
    nature_of_leave = db.Column(db.String)
    type_leave = db.Column(db.String)
    leave_letter_status = db.Column(db.Boolean)
    leave_reason = db.Column(db.String)
    created_on = db.Column(db.DateTime)
    created_by = db.Column(db.String)
    approved_by = db.Column(db.String)
