import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from plotnine import aes, facet_wrap, geom_bar, ggplot, ggsave, ggtitle, labs
from werkzeug.security import check_password_hash, generate_password_hash

plt.switch_backend("agg")


from flask_login import current_user, login_required, login_user, logout_user

import telegram_secrets
from forms import LoginForm, PaymentEditForm, SignupForm
from payment import Payment
from sqlite_excel import convert_input, export_database
from user import User


def favicon():
    return url_for("static", filename="favicon.ico")


def signup():
    form = SignupForm()
    if request.method == "GET":
        return render_template("signup.html", form=form)
    else:
        username = form.data["username"]
        password = form.data["password"]
        password_hash = generate_password_hash(password, method="sha256")

        user_db = current_app.config["user_db"]

        try:
            exist_name = user_db.get_user(username)
            old_username = exist_name.username
            if username == old_username:
                flash("Username already exists.")
                return redirect(url_for("signup"))
        except TypeError as e:
            user = User(username=username, password=password_hash)
            user_db.add_user(user)
            return redirect(url_for("login_page"))


def cd_list():

    cd_list = pd.read_excel("CD_list.xlsx")
    cd_list_filter = cd_list[["SL Name", "SL Code", "CD number", "Credit"]]
    cd_list_filter.sort_values(by="SL Name", ascending=False)
    return render_template(
        "cd.html",
        tables=[
            cd_list_filter.to_html(
                classes="table",
                border=1,
                table_id="table",
                justify="center",
                float_format="{:.0f}".format,
                header=True,
                index=False,
            )
        ],
    )


def pending_scroll_list():
    scroll_list = pd.read_csv("scroll_list.csv")
    scroll_list["Payment Received Date"] = pd.to_datetime(
        scroll_list["Payment Received Date"], format="%b %d, %Y %I:%M %p"
    )
    scroll_list["Payment Entry Date"] = pd.to_datetime(
        scroll_list["Payment Entry Date"], format="%b %d, %Y %I:%M %p"
    )
    scroll_list["Cheque Date"] = pd.to_datetime(
        scroll_list["Cheque Date"], format="%b %d, %Y %I:%M %p"
    )
    scroll_list["Date of Expiry"] = pd.to_datetime(
        scroll_list["Date of Expiry"], format="%b %d, %Y %I:%M %p"
    )

    scroll_list["Payment Received Date"] = scroll_list[
        "Payment Received Date"
    ].dt.strftime("%d-%m-%Y")
    scroll_list["Payment Entry Date"] = scroll_list["Payment Entry Date"].dt.strftime(
        "%d-%m-%Y"
    )
    scroll_list["Cheque Date"] = scroll_list["Cheque Date"].dt.strftime("%d-%m-%Y")
    scroll_list["Date of Expiry"] = scroll_list["Date of Expiry"].dt.strftime(
        "%d-%m-%Y"
    )
    scroll_list = scroll_list.rename({"Cheque Number": "Instrument number"}, axis=1)
    # cd_list_filter = cd_list[['SL Name','SL Code','CD number','Credit']]
    # cd_list_filter.sort_values(by='SL Name',ascending=False)
    return render_template(
        "scroll.html",
        tables=[
            scroll_list.to_html(
                classes="table",
                border=1,
                table_id="table",
                justify="center",
                float_format="{:.0f}".format,
                header=True,
                index=False,
            )
        ],
    )


def draw_chart(data):
    try:
        p = (
            ggplot(data=data)
            + aes(x="RM", fill="STATUS")
            + ggtitle("Underwriter/relationship manager breakup")
            + labs(x="Relationship manager", y="Count of tasks")
            + geom_bar()
            + facet_wrap(["UW"], ncol=3)
        )
        ggsave(
            p,
            filename="static/file.png",
            height=10,
            width=12,
            dpi=300,
            limitsize=False,
            verbose=False,
        )
    except:
        print("Error")

    return True


def home_page():

    conn = sqlite3.connect("payments.sqlite")
    data = pd.read_sql("SELECT * from payment", conn)
    copy_data = data[["ID", "STATUS", "RM", "UW"]].copy()
    copy_data.replace("", "_Unassigned", inplace=True)
    copy_data.fillna("_Unassigned", inplace=True)

    draw_chart(copy_data)

    pivot_data = pd.pivot_table(
        copy_data, index=["UW", "STATUS"], columns=["RM"], values="ID", aggfunc="count"
    )
    pivot_data.fillna(0, inplace=True)

    pivot_data = pivot_data.reset_index()

    pivot_data["Total"] = pivot_data.sum(numeric_only=True, axis=1)
    pivot_data.loc["TOTAL"] = pivot_data.sum(numeric_only=True, axis=0)

    conn.close()

    return render_template(
        "home.html",
        tables=[
            pivot_data.to_html(
                classes="table",
                border=1,
                table_id="table",
                na_rep="Total",
                justify="center",
                float_format="{:.0f}".format,
                header=True,
                index=False,
            )
        ],
        titles=pivot_data.columns.values,
    )


def download():
    path = export_database()
    download_string = "download" + datetime.now().strftime("%d%m%Y %H%M%S") + ".xlsx"
    path.to_excel(download_string, index=False)
    return send_file(download_string, download_name="download.xlsx", as_attachment=True)


def upload():
    if request.method == "POST":
        upload_file = request.files.get("file")
        convert_input(upload_file)
        flash("Payment data has been uploaded.")
    return render_template("upload.html")


def payments_all():
    db = current_app.config["db"]
    if request.method == "GET":
        payments = db.get_payments()
        return render_template("payments_all.html", payments=sorted(payments))

    else:
        if not current_user.is_admin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            db.delete_payment(int(form_payment_key))
        return redirect(url_for("payments_all"))


def payments_completed():
    db = current_app.config["db"]
    if request.method == "GET":
        payments = db.get_payments()
        return render_template("payments_completed.html", payments=sorted(payments))
    else:
        if not current_user.is_admin:
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
        if not current_user.is_admin:
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
        if not current_user.is_admin:
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

        proposal = form.data["proposal"]
        policyno = form.data["policyno"]
        instrumentno = form.data["instrumentno"]

        if underwriter != "":
            underwriter_history = "<br>" + created + ": Assigned to " + underwriter
            history = created + ": " + status + underwriter_history
        else:
            history = created + ": " + status

        if status == "Completed":
            completed = created
        else:
            completed = None
        payment = Payment(
            title,
            date=date,
            amount=amount,
            mode=mode,
            modeentry=modeentry,
            customerid=customerid,
            rel_manager=rel_manager,
            broker=broker,
            remarks=remarks,
            underwriter=underwriter,
            ticket=ticket,
            status=status,
            voucher=voucher,
            created=created,
            history=history,
            completed=completed,
            proposal=proposal,
            policyno=policyno,
            instrumentno=instrumentno,
        )
        db = current_app.config["db"]
        payment_key = db.add_payment(payment)

        CHAT_ID = telegram_secrets.CHAT_ID
        SEND_URL = telegram_secrets.SEND_URL

        try:
            string_date = date.strftime("%d-%m-%Y")
        except AttributeError as e:
            string_date = "None"
        message = """Payee name: {}
Amount received: {}
Date of payment: {}
Mode of payment: {}
Instrument number: {}
        """.format(
            title,
            amount,
            string_date,
            mode,
            instrumentno,
        )

        requests.post(SEND_URL, json={"chat_id": CHAT_ID, "text": message})

        return redirect(url_for("payment_page", payment_key=payment_key))
    return render_template("payment_edit.html", form=form)


def validate_payment_form():

    form.data = {}
    form.errors = {}

    form_title = form.get("title", "").strip()
    if len(form_title) == 0:
        form.errors["title"] = "Title can not be blank."
    else:
        form.data["title"] = form_title

    return len(form.errors) == 0


def compare_underwriter(dt_string, old_value, new_value):

    if old_value != new_value:
        if new_value != "":
            underwriter_update = "<br>" + dt_string + ": Assigned to " + new_value
        else:
            underwriter_update = "<br>" + dt_string + ": Task has been unassigned."
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

        proposal = form.data["proposal"]
        policyno = form.data["policyno"]
        instrumentno = form.data["instrumentno"]

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        update = dt_string + ": " + status

        if payment.history != None:
            if payment.status != form.data["status"]:
                underwriter_update = compare_underwriter(
                    dt_string, payment.underwriter, underwriter
                )
                history = payment.history + "<br>" + update + underwriter_update

            else:
                underwriter_update = compare_underwriter(
                    dt_string, payment.underwriter, underwriter
                )
                history = payment.history + underwriter_update

        else:
            underwriter_update = compare_underwriter(
                dt_string, payment.underwriter, underwriter
            )
            history = update + underwriter_update

        if status == "Completed":
            if payment.completed is not None:
                completed = payment.completed
            else:
                completed = dt_string
        else:
            completed = None

        payment = Payment(
            title,
            date=date,
            amount=amount,
            mode=mode,
            modeentry=modeentry,
            customerid=customerid,
            rel_manager=rel_manager,
            broker=broker,
            nature=nature,
            remarks=remarks,
            underwriter=underwriter,
            ticket=ticket,
            status=status,
            voucher=voucher,
            history=history,
            completed=completed,
            proposal=proposal,
            policyno=policyno,
            instrumentno=instrumentno,
        )
        db.update_payment(payment_key, payment)

        # flash("Payment data updated.")
        return redirect(url_for("payment_page", payment_key=payment_key))

    form.title.data = payment.customer

    form.date.data = datetime.strptime(payment.date, "%Y-%m-%d") if payment.date else ""
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

    form.proposal.data = payment.proposal
    form.policyno.data = payment.policyno
    form.instrumentno.data = payment.instrumentno

    return render_template("payment_edit.html", form=form)


def login_page():

    if current_user.is_authenticated:
        return redirect(url_for("home_page"))
    form = LoginForm()
    user_db = current_app.config["user_db"]
    if form.validate_on_submit():
        username = form.data["username"]
        user = user_db.get_user(username)
        if user is not None:
            password = form.data["password"]

            if check_password_hash(user.password, password):
                login_user(user)

                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            else:
                flash("Invalid credentials.")
    return render_template("login.html", form=form)


def logout_page():
    logout_user()
    # flash("You have logged out.")
    return redirect(url_for("home_page"))
