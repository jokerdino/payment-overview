import pandas as pd
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    IntegerRangeField,
    RadioField,
    SelectField,
    StringField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    NumberRange,
    Regexp,
    ValidationError,
)

rh_list = pd.read_excel("RH list.xlsx")
rh_list.DATE = pd.to_datetime(rh_list.DATE).dt.date
public_holiday_list = pd.read_excel("public_holiday_list.xlsx")
public_holiday_list.DATE = pd.to_datetime(public_holiday_list.DATE).dt.date


def numOfDays(date1, date2):
    return (date2 - date1).days


class EmployeeForm(FlaskForm):
    emp_number = IntegerField(
        "Employee number",
        validators=[NumberRange(min=10000, max=99999), DataRequired()],
    )
    name = StringField(
        "Name of employee",
        validators=[
            DataRequired(),
            Regexp(
                r"^[a-zA-Z .-]+$", flags=0, message="Name should contain letters only."
            ),
        ],
    )
    leave_as_on = DateField("Leave balance as on :", validators=[DataRequired()])
    casual_leave = DecimalField(
        "Enter casual leave balance: ",
        validators=[InputRequired(), NumberRange(min=0, max=12)],
    )
    earned_leave = StringField(
        "Enter earned leave balance: ",
        validators=[
            InputRequired(),
            Regexp(
                r"(?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?",
                flags=0,
                message="Earned leave is in incorrect format.",
            ),
        ],
    )

    sick_leave = IntegerField(
        "Enter sick leave balance: ",
        validators=[InputRequired(), NumberRange(min=0, max=240)],
    )
    restricted_holiday = IntegerField(
        "Enter restricted holiday balance: ",
        validators=[InputRequired(), NumberRange(min=0, max=2)],
    )


class EarnedLeaveForm(FlaskForm):
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")

    def validate_end_date(self, field):
        if field.data.weekday() > 5:
            raise ValidationError("End date cannot be a weekend.")
        if field.data < self.start_date.data:
            print("start is higher than end")
            raise ValidationError("End date should not be earlier than start date.")
        if (numOfDays(self.start_date.data, field.data) + 1) > 120:
            raise ValidationError("Maximum earned leave allowed is 120 days.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("End date cannot be a public holiday.")

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            print("start is weekend")
            raise ValidationError("Start date cannot be a weekend.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be a public holiday.")


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

    def validate_end_date(self, field):
        if field.data.weekday() > 5:
            raise ValidationError("End date cannot be a weekend.")
        if field.data < self.start_date.data:
            # print("start is higher than end")
            raise ValidationError("End date should not be earlier than start date.")
        if (numOfDays(self.start_date.data, field.data) + 1) > 5:
            raise ValidationError("maximum CL allowed is 5 days.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("End date cannot be public holiday.")
        if self.type_leave.data == "half":
            if not field.data == self.start_date.data:
                raise ValidationError(
                    "For half day CL, end date should be same as start date."
                )

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            print("start is weekend")
            raise ValidationError("Start date cannot be a weekend.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be public holiday.")


class SickLeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave",
        choices=[("full", "Full pay"), ("half", "Half pay")],
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted:")

    def validate_end_date(self, field):
        if field.data.weekday() > 5:
            raise ValidationError("End date cannot be a weekend.")
        if field.data < self.start_date.data:
            print("start is higher than end")
            raise ValidationError("End date should not be earlier than start date.")
        if (numOfDays(self.start_date.data, field.data) + 1) > 120:
            raise ValidationError("Maximum sick leave allowed is 120 days.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("End date cannot be a public holiday.")

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            print("start is weekend")
            raise ValidationError("Start date cannot be a weekend.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be a public holiday.")


class SpecialLeaveForm(FlaskForm):
    leave_list = [
        ("Maternity", "Maternity Leave"),
        ("Paternity", "Paternity leave"),
        ("Quarantine", "Quarantine Leave"),
        ("Joining", "Joining leave"),
        ("Others", "Others"),
    ]
    type_leave = SelectField(
        "Enter type of leave", choices=leave_list, validators=[DataRequired()]
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")

    def validate_end_date(self, field):
        if field.data.weekday() > 5:
            raise ValidationError("End date cannot be a weekend.")
        if field.data < self.start_date.data:
            # print("start is higher than end")
            raise ValidationError("End date should not be earlier than start date.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("End date cannot be a public holiday.")

        if self.type_leave.data == "Joining":
            if (numOfDays(self.start_date.data, field.data) + 1) > 6:
                raise ValidationError("maximum joining leave allowed is 6 days.")
        elif self.type_leave.data == "Maternity":
            if (numOfDays(self.start_date.data, field.data) + 1) > 180:
                raise ValidationError("maximum maternity leave allowed is 180 days.")
        elif self.type_leave.data == "Paternity":
            if (numOfDays(self.start_date.data, field.data) + 1) > 15:
                raise ValidationError("maximum paternity leave allowed is 15 days.")

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            print("start is weekend")
            raise ValidationError("Start date cannot be a weekend.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be a public holiday.")


class LOPLeaveForm(FlaskForm):
    type_leave = RadioField(
        "Enter type of leave", choices=[("LOP", "LOP"), ("Strike", "Strike")]
    )
    start_date = DateField("Enter start date: ", validators=[DataRequired()])
    end_date = DateField("Enter end date: ", validators=[DataRequired()])
    leave_letter = BooleanField("Leave letter has been submitted: ")

    def validate_end_date(self, field):
        if field.data.weekday() > 5:
            raise ValidationError("End date cannot be a weekend.")
        if field.data < self.start_date.data:
            # print("start is higher than end")
            raise ValidationError("End date should not be earlier than start date.")

        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("End date cannot be public holiday.")

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            #            print("start is weekend")
            raise ValidationError("Start date cannot be a weekend.")
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be a public holiday.")


class RestrictedLeaveform(FlaskForm):
    start_date = DateField(
        "Enter restricted holiday date: ", validators=[DataRequired()]
    )
    leave_letter = BooleanField("Leave letter has been submitted: ")

    def validate_start_date(self, field):
        if field.data.weekday() > 5:
            print("start is weekend")
            raise ValidationError("Entered date cannot be a weekend.")
        if not (rh_list["DATE"] == field.data).any():
            raise ValidationError("Entered date should be restricted holiday.")
        # print(rh_list['DATE'])
        # print(field.data)
        if (public_holiday_list["DATE"] == field.data).any():
            raise ValidationError("Start date cannot be a public holiday.")


class ReportDateForm(FlaskForm):
    start_date = DateField("Enter date: ", validators=[DataRequired()])
