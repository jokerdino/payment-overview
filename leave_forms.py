from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    IntegerRangeField,
    RadioField,
    SelectField,
    StringField,
)
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


class EarnedLeaveForm(FlaskForm):
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")


class CalculateEarnedLeaveForm(FlaskForm):

    start_date = DateField(
        "Enter date upto which Earned leave is to be calculated: ",
        validators=[DataRequired()],
    )


class LeaveEncashmentForm(FlaskForm):

    block_year_list = [
        ("2022-2023", "2022-2023"),
        ("2024-2025", "2024-2025"),
        ("2026-2027", "2026-2027"),
    ]
    block_year = SelectField(
        "Select block year for which leave is encashed:",
        choices=block_year_list,
        validators=[DataRequired()],
    )
    start_date = DateField(
        "Enter date of leave encashment: ", validators=[DataRequired()]
    )
    encashed_days = IntegerRangeField("Enter number of days: ", default=15)


class CasualLeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave",
        choices=[("full", "Full day CL"), ("half", "Half day CL")],
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted:")


class SickLeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave",
        choices=[("full", "Full pay"), ("half", "Half pay")],
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted:")


class SpecialLeaveForm(FlaskForm):
    leave_list = [
        ("Maternity", "Maternity Leave"),
        ("Paternity", "Paternity leave"),
        ("Quarantine", "Quarantine Leave"),
        ("Exam", "Examination leave"),
        ("Others", "Others"),
    ]
    type_leave = SelectField(
        "Enter type of leave", choices=leave_list, validators=[DataRequired()]
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")


class LOPLeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave", choices=[("LOP", "LOP"), ("Strike", "Strike")]
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")


class RestrictedLeaveform(FlaskForm):
    start_date = DateField(
        "Enter restricted holiday date: ", validators=[DataRequired()]
    )
    leave_letter = BooleanField("Leave letter has been submitted: ")


class ReportDateForm(FlaskForm):
    start_date = DateField("Enter date: ", validators=[DataRequired()])
