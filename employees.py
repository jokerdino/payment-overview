from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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

    def __repr__(self):
        return f"<Employee {self.emp_number!r}: {self.name!r}>"


# def __init__(self, emp_id, name, leave_as_on, count_casual_leave, count_earned_leave, count_sick_leave, count_restricted_holiday):
#    self.emp_id = emp_id
#    self.name = name
#    self.leave_as_on = leave_as_on
#    self.count_casual_leave = count_casual_leave
#    self.count_earned_leave = count_earned_leave
#    self.count_sick_leave = count_sick_leave
#    self.count_restricted_history = count_restricted_holiday
#


class Leaves(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    # emp_id = db.Column(db.Integer, db.ForeignKey("employee.id"))
    emp_number = db.Column(db.Integer, db.ForeignKey("employee.emp_number"))
    date_of_leave = db.Column(db.String)
    nature_of_leave = db.Column(db.String)
    type_leave = db.Column(db.String)
    leave_letter_status = db.Column(db.String)
