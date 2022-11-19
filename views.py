from datetime import datetime

from flask import current_app, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from passlib.hash import pbkdf2_sha256 as hasher

from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required

from forms import LoginForm, PaymentEditForm
from user import get_user
from payment import Payment



def home_page():
    return render_template("home.html")


def payments_page():
    db = current_app.config["db"]
    payments = db.get_payments()
    return render_template("payments.html", payments=sorted(payments))



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
        payment = Payment(title, date=date)
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


@login_required
def payment_edit_page(payment_key):

    db = current_app.config["db"]
    payment = db.get_payment(payment_key)
    form = PaymentEditForm()
    if form.validate_on_submit():
        title = form.data["title"]
        date = form.data["date"]
        payment = Payment(title, date=date)
        db.update_payment(payment_key, payment)
        flash("Payment data updated.")
        return redirect(url_for("payment_page", payment_key = payment_key))
    form.title.data = payment.customer
    form.date.data = datetime.strptime(payment.date, '%Y-%m-%d') if payment.date else ""
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
                flash("You have logged in.")
                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            flash("Invalid credentials.")
    return render_template("login.html",form=form)

def logout_page():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("home_page"))
