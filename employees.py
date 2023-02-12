from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()


# from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    emp_number = db.Column(db.Integer, db.ForeignKey("employee.emp_number"))
    employee = db.relationship("Employee", backref=db.backref("user", uselist=False))
    is_admin = db.Column(db.Boolean)
    reset_code = db.Column(db.Integer)
    reset_password_page = db.Column(db.Boolean)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return True

    def is_authenticated(self):
        return True


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_number = db.Column(db.Integer)
    name = db.Column(db.String(80), nullable=False)
    leave_as_on = db.Column(db.String(80))
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


# def __repr__(self):
#    return f"<Employee {self.emp_number!r}: {self.name!r}>"


class Leaves(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    emp_number = db.Column(db.Integer, db.ForeignKey("employee.emp_number"))
    employee = db.relationship(
        "Employee", backref=db.backref("employee", uselist=False)
    )
    date_of_leave = db.Column(db.String)
    nature_of_leave = db.Column(db.String)
    type_leave = db.Column(db.String)
    leave_letter_status = db.Column(db.String)
    leave_reason = db.Column(db.String)
    created_on = db.Column(db.String)
    created_by = db.Column(db.String)
