from datetime import datetime

from flask import current_app, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from passlib.hash import pbkdf2_sha256 as hasher

import pandas as pd
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required

from forms import LoginForm, PaymentEditForm
from user import get_user
from payment import Payment
from sqlite_excel import convert_input


def favicon():
    return url_for('static', filename='favicon.ico')


def home_page():
    return render_template("home.html")

def upload():
    if request.method == 'POST':
        upload_file = request.files.get('file')
        convert_input(upload_file)
        flash("Payment data has been uploaded.")
#        return redirect(url_for("payments_page"))
    return render_template('upload.html')

def payments_completed():
    db = current_app.config["db"]
    if request.method == "GET":
        payments = db.get_payments()
        return render_template("payments_completed.html", payments=sorted(payments))
    else:
        if not current_user.is_superadmin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            db.delete_payment(int(form_payment_key))
        return redirect(url_for("payments_completed"))

def payments_pending_uw():
    db = current_app.config["db"]
    if request.method == "GET":
        payments = db.get_payments()
        return render_template("payments_pending_uw.html", payments=sorted(payments))
    else:
        if not current_user.is_superadmin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            db.delete_payment(int(form_payment_key))
        return redirect(url_for("payments_pending_uw"))

def payments_page():
    db = current_app.config["db"]
    if request.method == "GET":
        payments = db.get_payments()
        return render_template("payments_table.html", payments=sorted(payments))
    else:
        if not current_user.is_superadmin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            db.delete_payment(int(form_payment_key))
        return redirect(url_for("payments_page"))


def payment_page(payment_key):
    db = current_app.config["db"]
    payment = db.get_payment(payment_key)
    return render_template("payment.html", payment=payment)

@login_required
def payment_add_page():
    form = PaymentEditForm()
    if form.validate_on_submit():

        title = form.data["title"]
        date = form.data["date"]
        amount = form.data["amount"]
        mode = form.data["mode"]

        modeentry = form.data["modeentry"]
        rel_manager = form.data["rel_manager"]
        broker = form.data["broker"]

        remarks = form.data["remarks"]
        underwriter = form.data["underwriter"]
        status = form.data["status"]

        ticket = form.data["ticket"]
        customerid = form.data["customerid"]

        voucher = form.data["voucher"]
        created_date = datetime.now()
        created = created_date.strftime("%d/%m/%Y %H:%M:%S")

        if underwriter != "":
            underwriter_history = "<br>"+created + ": Assigned to " + underwriter
            history = created + ": "+ status +underwriter_history
        else:
            history = created + ": "+ status

        if status == "Completed":
            completed = created
        else:
            completed = None
        payment = Payment(title, date=date, amount=amount, mode= mode,
                modeentry=modeentry, customerid=customerid, rel_manager=rel_manager,broker=broker,
                remarks = remarks, underwriter = underwriter, ticket=ticket, status=status,
                voucher=voucher, created = created, history = history, completed = completed)
        db = current_app.config["db"]
        payment_key = db.add_payment(payment)
        return redirect(url_for("payment_page", payment_key=payment_key))
    return render_template("payment_edit.html", form=form)

def validate_payment_form():

    form.data = {}
    form.errors = {}

    form_title = form.get("title", "").strip()
    if len(form_title) ==0:
        form.errors["title"] = "Title can not be blank."
    else:
        form.data["title"] = form_title

    return len(form.errors) == 0


def compare_underwriter(dt_string,old_value, new_value):

    if old_value != new_value:
        if new_value != "":
            underwriter_update =  '<br>'+dt_string + ": Assigned to " + new_value
        else:
            underwriter_update =  '<br>'+dt_string +": Task has been unassigned."
        return underwriter_update
    else:
        return ""

@login_required
def payment_edit_page(payment_key):

    db = current_app.config["db"]
    payment = db.get_payment(payment_key)
    form = PaymentEditForm()

    if form.validate_on_submit():
        title = form.data["title"]
        date = form.data["date"]
        amount = form.data["amount"]

        mode = form.data["mode"]
        modeentry = form.data["modeentry"]
        customerid = form.data["customerid"]
        rel_manager = form.data["rel_manager"]

        broker = form.data["broker"]
        nature = form.data["nature"]
        remarks = form.data["remarks"]
        underwriter = form.data["underwriter"]

        ticket = form.data["ticket"]
        status = form.data["status"]
        voucher = form.data["voucher"]

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        update = dt_string +  ': ' +status

        if payment.history != None:
            if payment.status != form.data['status']:
                underwriter_update = compare_underwriter(dt_string, payment.underwriter, underwriter)
                history = payment.history +'<br>'+update+underwriter_update

            else:
                underwriter_update = compare_underwriter(dt_string, payment.underwriter, underwriter)
                history = payment.history + underwriter_update

        else:
            underwriter_update = compare_underwriter(dt_string, payment.underwriter, underwriter)
            history = update + underwriter_update

        if status == "Completed":
            completed = dt_string
        else:
            completed = None

        payment = Payment(title, date=date, amount=amount, mode = mode,
                modeentry=modeentry, customerid= customerid, rel_manager=rel_manager, broker=broker,
                nature=nature,remarks=remarks,underwriter=underwriter,
                ticket=ticket, status=status, voucher=voucher, history = history, completed = completed)
        db.update_payment(payment_key, payment)

        #flash("Payment data updated.")
        return redirect(url_for("payment_page", payment_key = payment_key))

    form.title.data = payment.customer

    form.date.data = datetime.strptime(payment.date, '%Y-%m-%d') if payment.date else ""
    form.amount.data = payment.amount
    form.mode.data = payment.mode
    form.modeentry.data = payment.modeentry

    form.customerid.data = payment.customerid
    form.rel_manager.data = payment.rel_manager
    form.broker.data = payment.broker
    form.nature.data = payment.nature

    form.remarks.data = payment.remarks
    form.underwriter.data = payment.underwriter
    form.ticket.data = payment.ticket

    form.status.data = payment.status
    form.voucher.data = payment.voucher
    form.history.data = payment.history

    return render_template ("payment_edit.html", form=form)

def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.data["username"]
        user = get_user(username)
        if user is not None:
            password = form.data["password"]
            if hasher.verify(password, user.password):
                login_user(user)
    #            flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
     #       flash("Invalid credentials.")
    return render_template("login.html",form=form)

def logout_page():
    logout_user()
   # flash("You have logged out.")
    return redirect(url_for("home_page"))
