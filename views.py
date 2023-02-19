from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
from flask import flash, redirect, render_template, request, send_file, url_for
from plotnine import aes, facet_wrap, geom_bar, ggplot, ggsave, ggtitle, labs
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

plt.switch_backend("agg")


from flask_login import current_user, login_required, login_user, logout_user

import telegram_secrets
import user_views
from forms import LoginForm, PaymentEditForm, SignupForm
from model import Payment, User
from sqlite_excel import convert_input, export_database


def favicon():
    return url_for("static", filename="favicon.ico")


def cd_list():

    cd_list = pd.read_excel("CD_list.xlsx")
    cd_list_filter = cd_list[["SL Name", "SL Code", "CD number", "Credit"]]
    cd_list_filter.sort_values(by="SL Name", ascending=False)
    return render_template(
        "cd.html",
        tables=[
            cd_list_filter.to_html(
                classes="table is-fullwidth",
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
    scroll_list = pd.read_csv("dw_461_pending_scroll_reg.csv")
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
    ].dt.strftime("%Y-%m-%d")
    scroll_list["Payment Entry Date"] = scroll_list["Payment Entry Date"].dt.strftime(
        "%Y-%m-%d"
    )
    scroll_list["Cheque Date"] = scroll_list["Cheque Date"].dt.strftime("%Y-%m-%d")
    scroll_list["Date of Expiry"] = scroll_list["Date of Expiry"].dt.strftime(
        "%Y-%m-%d"
    )
    scroll_list = scroll_list.rename({"Cheque Number": "Instrument number"}, axis=1)
    # cd_list_filter = cd_list[['SL Name','SL Code','CD number','Credit']]
    # cd_list_filter.sort_values(by='SL Name',ascending=False)
    return render_template(
        "scroll.html",
        tables=[
            scroll_list.to_html(
                classes="table is-fullwidth",
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
            + aes(x="rel_manager", fill="status")
            + ggtitle("Underwriter/relationship manager breakup")
            + labs(x="Relationship manager", y="Count of tasks")
            + geom_bar()
            + facet_wrap(["underwriter"], ncol=3)
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

    from server import db

    df = pd.read_sql(
        db.session.query(Payment).statement,
        db.get_engine(),
    )

    copy_data = df[["id", "status", "rel_manager", "underwriter"]].copy()
    copy_data.replace("", "_Unassigned", inplace=True)
    copy_data.fillna("_Unassigned", inplace=True)

    draw_chart(copy_data)

    pivot_data = pd.pivot_table(
        copy_data,
        index=["underwriter", "status"],
        columns=["rel_manager"],
        values="id",
        aggfunc="count",
    )
    pivot_data.fillna(0, inplace=True)

    pivot_data = pivot_data.reset_index()

    pivot_data["Total"] = pivot_data.sum(numeric_only=True, axis=1)
    pivot_data.loc["TOTAL"] = pivot_data.sum(numeric_only=True, axis=0)

    return render_template(
        "home.html",
        tables=[
            pivot_data.to_html(
                classes="table is-fullwidth",
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
    from server import db

    if request.method == "GET":
        return render_template("payments_all.html", payments=Payment.query.all())

    else:
        if not current_user.is_admin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            Payment.query.filter(Payment.id == form_payment_key).delete()
            db.session.commit()
        return redirect(url_for("payments_all"))


def payments_completed():
    from server import db

    if request.method == "GET":
        return render_template(
            "payments_completed.html",
            payments=Payment.query.filter(Payment.status == "Completed").all(),
        )
    else:
        if not current_user.is_admin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            Payment.query.filter(Payment.id == form_payment_key).delete()
            db.session.commit()
        return redirect(url_for("payments_completed"))


def payments_pending_uw():
    from server import db

    if request.method == "GET":

        return render_template(
            "payments_pending_uw.html",
            payments=Payment.query.filter(
                Payment.status != "Completed",
                Payment.status != "To be receipted",
                Payment.status != "Waiting for payment",
                Payment.status != "To be refunded",
            ).all(),
        )
    else:
        if not current_user.is_admin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            Payment.query.filter(Payment.id == form_payment_key).delete()
            db.session.commit()
        return redirect(url_for("payments_pending_uw"))


def payments_page():
    from server import db

    if request.method == "GET":

        return render_template(
            "payments_table.html",
            payments=Payment.query.filter(
                or_(
                    Payment.status == "To be receipted",
                    Payment.status == "Waiting for payment",
                    Payment.status == "To be refunded",
                )
            ).all(),
        )

    else:
        if not current_user.is_admin:
            abort(401)
        form_payment_keys = request.form.getlist("payment_keys")
        for form_payment_key in form_payment_keys:
            Payment.query.filter(Payment.id == form_payment_key).delete()
            db.session.commit()
        return redirect(url_for("payments_page"))


def payment_page(payment_key):
    payment = Payment.query.get_or_404(payment_key)
    return render_template("payment.html", payment=payment)


@login_required
def payment_add_page():
    from server import db

    form = PaymentEditForm()
    if form.validate_on_submit():

        customer = form.data["customer"]
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
            customer=customer,
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
        db.session.add(payment)
        db.session.commit()
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
            customer,
            amount,
            string_date,
            mode,
            instrumentno,
        )

        requests.post(SEND_URL, json={"chat_id": CHAT_ID, "text": message})

        return redirect(url_for("payment_page", payment_key=payment.id))
    return render_template("payment_edit.html", form=form)


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

    from server import db

    payment = Payment.query.get_or_404(payment_key)
    form = PaymentEditForm()

    if form.validate_on_submit():
        customer = form.data["customer"]
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
            customer=customer,
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
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for("payment_page", payment_key=payment.id))

    form.customer.data = payment.customer

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


def signup():
    from server import db

    form = SignupForm()

#    if request.method == "GET":
#        return render_template("signup.html", form=form)
    if request.method == "POST":
        username = form.data["username"]
        password = form.data["password"]
        password_hash = generate_password_hash(password, method="sha256")

        emp_number = form.data["emp_number"]

        user = User.query.filter(
            or_(User.username == username, User.emp_number == emp_number)
        ).first()
        if user:
            flash("Username or employee number already exists.")
            # return redirect(url_for("signup"))

        else:
            user = User(
                username=username, password=password_hash, emp_number=emp_number
            )
            db.session.add(user)
            user_views.admin_check()
            db.session.commit()

            return redirect(url_for("login_page"))
    return render_template("signup.html", form=form)


def login_page():

    if current_user.is_authenticated:
        return redirect(url_for("home_page"))
    form = LoginForm()

    from server import db

    if form.validate_on_submit():
        username = form.data["username"]
        user = db.session.query(User).filter(User.username == username).first()
        if user is not None:
            password = form.data["password"]

            if check_password_hash(user.password, password):
                login_user(user)

                next_page = request.args.get("next", url_for("home_page"))
                return redirect(next_page)
            else:
                flash("Invalid credentials.")
        else:
            flash("Invalid credentials.")
    return render_template("login.html", form=form)


def logout_page():
    logout_user()
    # flash("You have logged out.")
    return redirect(url_for("home_page"))
