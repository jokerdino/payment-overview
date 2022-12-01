from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField, SelectField

from datetime import datetime

class PaymentEditForm(FlaskForm):
    title = StringField("Customer name:", validators = [DataRequired()])

    date = DateField("Date:", validators=[Optional(),],)
    amount = IntegerField("Amount:",validators=[Optional(),])
    mode = SelectField('Mode of payment:', coerce=str, choices=[('',''),('NEFT','NEFT'),('Cheque','Cheque'),('Cash','Cash'),('Others','Others')])

    modeentry_list = [('',''),('CD','CD'),('Regular','Regular'),('Scroll','Scroll'),('BG','BG'),('Others','Others')]
    rel_manager_list = [('',''),('Kannan','Kannan'),('Ravikumar','Ravikumar'),('Varinder Singh','Varinder Singh')]
    nature_list = [('',''),
            ('Fresh','Fresh'),
            ('Renewal','Renewal'),
            ('Endorsement','Endorsement'),
            ('Installment','Installment'),
            ('Extension','Extension'),
            ('Incoming coinsurance','Incoming coinsurance'),
            ('Others','Others')]

    underwriter_list = [('',''),
            ('Anand Kumar','Anand Kumar'),
            ('Kesavi','Kesavi'),
            ('Anupriya','Anupriya'),
            ('Swatee Barik','Swatee Barik'),
            ('Vijaya','Vijaya'),
            ('Naval Jacob','Naval Jacob'),
            ('Others','Others')]
    status_list = [
            ('To be receipted','To be receipted'),
            ('To be underwritten','To be underwritten'),
            ('Work in progress','Work in progress'),
            ('Awaiting further details from brokers/insured',
                'Awaiting further details from brokers/insured'),
            ('Approval pending','Approval pending'),
            ('GC Core issue - ticket raised','GC Core issue - ticket raised'),
            ('Completed','Completed'),
            ('Others1','Others1'),
            ('Others2','Others2')]

    modeentry = SelectField('Mode of entry:', coerce=str, choices=modeentry_list)
    customerid = IntegerField("Customer ID:", validators=[Optional(),])
    rel_manager = SelectField("Relationship manager:",coerce=str,choices=rel_manager_list)

    broker = StringField("Broker:", validators=[Optional(),])
    nature = SelectField("Nature of proposal:", coerce=str, choices=nature_list,validators=[Optional(),])
    underwriter = SelectField("Underwriter:",coerce=str,choices=underwriter_list, validators=[Optional(),])
    status = SelectField("Status:",coerce=str,choices=status_list,validators=[Optional(),])
    ticket = StringField("Ticket:",validators=[Optional(),])
    remarks = StringField("Remarks:",validators=[Optional(),])
    voucher = StringField("Voucher number:")
    created = StringField("Created on:")
    history = StringField("Status updates:")

    proposal = StringField("Proposal number: ")
    policyno = StringField("Policy number: ")

class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])

    password = PasswordField("Password", validators=[DataRequired()])

