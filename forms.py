from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField

from datetime import datetime

class PaymentEditForm(FlaskForm):
    title = StringField("Title", validators = [DataRequired()])

    date = DateField(
            "Date",
            validators=[Optional(),
                ],
            )




class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

