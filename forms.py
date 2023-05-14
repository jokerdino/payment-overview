from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange, Optional


class PaymentEditForm(FlaskForm):
    customer = StringField("Customer name:", validators=[DataRequired()])

    date = DateField(
        "Date:",
        validators=[
            Optional(),
        ],
    )
    amount = StringField(
        "Amount:",
        validators=[
            Optional(),
        ],
    )
    mode_list = ["", "NEFT", "Cheque", "Cash", "Others"]
    mode = SelectField("Mode of payment:", choices=mode_list)
    modeentry_list = ["", "CD", "Regular", "Scroll", "BG", "Others"]
    rel_manager_list = ["", "Kannan", "Ravikumar", "Varinder", "Anand Kumar"]
    nature_list = [
        "",
        "Fresh",
        "Renewal",
        "Endorsement",
        "Installment",
        "Extension",
        "Incoming coinsurance",
        "Others",
    ]
    underwriter_list = [
        "",
        "Anand Kumar",
        "Kesavi",
        "Pradeep",
        "Swatee Barik",
        "Vijaya",
        "Naval Jacob",
        "Others",
    ]
    status_list = [
        "To be receipted",
        "To be underwritten",
        "Work in progress",
        "Awaiting further details from brokers/insured",
        "Approval pending",
        "GC Core issue - Ticket raised",
        "Completed",
        "To be refunded",
        "Waiting for payment",
        "Others1",
        "Others2",
    ]

    modeentry = SelectField("Mode of entry:", choices=modeentry_list)
    customerid = StringField(
        "Customer ID:",
        validators=[
            Optional(),
        ],
    )
    rel_manager = SelectField("Relationship manager:", choices=rel_manager_list)

    broker = StringField(
        "Broker:",
        validators=[
            Optional(),
        ],
    )
    nature = SelectField(
        "Nature of proposal:",
        choices=nature_list,
        validators=[
            Optional(),
        ],
    )
    underwriter = SelectField(
        "Underwriter:",
        choices=underwriter_list,
        validators=[
            Optional(),
        ],
    )
    status = SelectField(
        "Status:",
        choices=status_list,
        validators=[
            Optional(),
        ],
    )
    ticket = StringField(
        "Ticket:",
        validators=[
            Optional(),
        ],
    )
    remarks = TextAreaField(
        "Remarks:",
        validators=[
            Optional(),
        ],
    )
    voucher = StringField("Voucher number:")
    created = StringField("Created on:")
    history = StringField("Status updates:")

    proposal = StringField("Proposal number: ")
    policyno = StringField("Policy number: ")
    instrumentno = StringField("Instrument number: ")


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    emp_number = IntegerField(
        "Employee number",
        validators=[NumberRange(min=10000, max=99999), DataRequired()],
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class UpdateUserForm(FlaskForm):
    is_admin = BooleanField("Make the user admin: ")
    reset_password_page = BooleanField("Enable password reset page: ")


class ResetPasswordForm(FlaskForm):
    username = StringField("Enter username:", validators=[DataRequired()])
    emp_number = IntegerField("Enter employee number: ", validators=[DataRequired()])
    #  reset_code = IntegerField("Enter reset code received from admin: ", validators=[DataRequired()])
    password = PasswordField("Enter new password: ", validators=[DataRequired()])
