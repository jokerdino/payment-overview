from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField, SelectField

from datetime import datetime

class PaymentEditForm(FlaskForm):
    title = StringField("Title", validators = [DataRequired()])

    date = DateField(
            "Date",
            validators=[Optional(),
                ],
            )
    amount = IntegerField("Amount",validators=[Optional(),])
    mode = StringField("Mode of payment", validators=[Optional(),])

    modeentry_list = ['CD', 'Scroll']
    modeentry = StringField("Mode of entry", validators=[Optional(),])

    rel_manager = StringField("Relationship manager", validators=[Optional(),])
    broker = StringField("Broker", validators=[Optional(),])
    nature = StringField("Nature", validators=[Optional(),])
    underwriter = StringField("Underwriter",validators=[Optional(),])
    status = StringField("Status",validators=[Optional(),])
    ticket = StringField("Ticket",validators=[Optional(),])
    remarks = StringField("Remarks",validators=[Optional(),])
    customerid = IntegerField("customerid",validators=[Optional(),])
    cdnumber = StringField("cdnumber",validators=[Optional(),])

class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

