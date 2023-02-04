from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, RadioField, StringField
from wtforms.validators import DataRequired


class EmployeeForm(FlaskForm):
    emp_number = StringField("Employee number", validators=[DataRequired()])
    name = StringField("Name of employee", validators=[DataRequired()])
    leave_as_on = DateField("Leave balance as on :", validators=[DataRequired()])
    casual_leave = StringField(
        "Enter casual leave balance: ", validators=[DataRequired()]
    )
    earned_leave = StringField(
        "Enter earned leave balance: ", validators=[DataRequired()]
    )
    sick_leave = IntegerField("Enter sick leave balance: ", validators=[DataRequired()])
    restricted_holiday = IntegerField(
        "Enter restricted holiday balance: ", validators=[DataRequired()]
    )


class LeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave",
        choices=[("full", "Full day CL"), ("half", "Half day CL")],
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted:")
