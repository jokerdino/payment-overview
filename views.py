from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
from flask import flash, redirect, render_template, request, send_file, url_for
from plotnine import (
    aes,
    element_text,
    facet_wrap,
    geom_bar,
    ggplot,
    ggsave,
    ggtitle,
    labs,
    theme,
)
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

plt.switch_backend("agg")


from flask_login import current_user, login_required, login_user, logout_user

import telegram_secrets
import user_views
from forms import LoginForm, PaymentEditForm, SignupForm
from model import Config, Employee, Payment, User
from sqlite_excel import convert_input, export_database


def favicon():
    return url_for("static", filename="favicon.ico")


def home():
    return render_template("home.html")


def downloaded_items():
    receipted_items = pd.read_sql(
        "receipted", "postgresql://barneedhar:barneedhar@localhost:5432/payments"
    )
    receipted_items = receipted_items[
        ["id", "customer", "date", "amount", "instrumentno", "status"]
    ]
    return render_template(
        "payments_receipted.html",
        receipted_tables=receipted_items.to_dict(orient="records"),
    )


def upload_cd_list():
    from server import db

    if request.method == "POST":
        cd_file = request.files.get("file")
        cd_list = pd.read_excel(cd_file)
        cd_list_filter = cd_list[["SL Name", "SL Code", "CD number", "Credit"]]
        engine = "postgresql://barneedhar:barneedhar@localhost:5432/payments"
        cd_list_filter.to_sql("cd_list", engine, if_exists="replace", index=False)
        config = Config.query.first()
        config.cd_list_updated_time = datetime.now()
        db.session.commit()
        flash("CD list has been uploaded.")
    return render_template("upload.html", title="Upload CD list")


def cd_list():
    cd_list_filter = pd.read_sql(
        "cd_list", "postgresql://barneedhar:barneedhar@localhost:5432/payments"
    )
    cd_header_list = list(cd_list_filter.columns.values)
    config = Config.query.first()
    return render_template(
        "cd_new.html",
        receipted_tables=cd_list_filter.to_dict(orient="records"),
        header=cd_header_list,
        updated_time=config.cd_list_updated_time,
    )


def upload_scroll_list():
    from server import db

    if request.method == "POST":
        scroll_file = request.files.get("file")
        scroll_list = pd.read_csv(scroll_file)
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
        scroll_list.loc[scroll_list["Cheque Date"].isna(), "Cheque Date"] = scroll_list[
            "Payment Entry Date"
        ]
        scroll_list = scroll_list.rename({"Cheque Number": "Instrument number"}, axis=1)
        engine = "postgresql://barneedhar:barneedhar@localhost:5432/payments"
        scroll_list.to_sql("scroll_list", engine, if_exists="replace", index=False)
        config = Config.query.first()
        config.scroll_updated_time = datetime.now()
        db.session.commit()
        flash("Pending scroll list has been uploaded.")
    return render_template("upload.html", title="Upload pending scroll list")


def pending_scroll_list():
    scroll_list = pd.read_sql(
        "scroll_list", "postgresql://barneedhar:barneedhar@localhost:5432/payments"
    )
    scroll_header_list = list(scroll_list.columns.values)
    config = Config.query.first()
    return render_template(
        "scroll_list.html",
        tables=scroll_list.to_dict(orient="records"),
        header=scroll_header_list,
        updated_time=config.scroll_updated_time,
    )


def draw_chart():
    data = prepare_data()
    try:
        p = (
            ggplot(data=data)
            + aes(x="rel_manager", fill="status")
            + ggtitle("Underwriter/relationship manager breakup")
            + labs(x="Relationship manager", y="Count of tasks")
            + geom_bar()
            + facet_wrap(["underwriter"], ncol=3)
            + theme(axis_text_x=element_text(angle=90, hjust=1))
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
        return send_file("static/file.png", mimetype="image/png")
    except:
        print("Error")


def prepare_data():
    from server import db

    df = pd.read_sql(
        db.session.query(Payment).statement,
        db.get_engine(),
    )

    copy_data = df[["id", "status", "rel_manager", "underwriter"]].copy()
    copy_data.replace("", "_Unassigned", inplace=True)
    copy_data.fillna("_Unassigned", inplace=True)
    return copy_data


def home_page():
    copy_data = prepare_data()

    pivot_data = pd.pivot_table(
        copy_data,
        index=["underwriter", "status"],
        columns=["rel_manager"],
        values="id",
        aggfunc="count",
    )

    pivot_data = pivot_data.reset_index()

    pivot_data["Total"] = pivot_data.sum(numeric_only=True, axis=1)

    pivot_header_list = list(pivot_data.columns.values)
    return render_template(
        "underwriting_home.html",
        tables=pivot_data.to_dict(orient="records"),
        header=pivot_header_list,
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
    return render_template("upload.html", title="Upload NEFT file from NEFT portal")


def payments_all():
    from server import db

    if request.method == "GET":
        return render_template(
            "payments_all.html", payments=Payment.query.all(), title="All the payments"
        )

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
            "payments_all.html",
            payments=Payment.query.filter(Payment.status == "Completed").all(),
            title="Completed proposals",
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
            "payments_all.html",
            payments=Payment.query.filter(
                Payment.status != "Completed",
                Payment.status != "To be receipted",
                Payment.status != "Waiting for payment",
                Payment.status != "To be refunded",
            ).all(),
            title="Payments pending for underwriting",
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
            "payments_all.html",
            payments=Payment.query.filter(
                or_(
                    Payment.status == "To be receipted",
                    Payment.status == "Waiting for payment",
                    Payment.status == "To be refunded",
                )
            ).all(),
            title="Payments to be receipted",
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

        if payment.history is not None:
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

        # payment = Payment(
        payment.customer = customer
        payment.date = date
        payment.amount = amount
        payment.mode = mode
        payment.modeentry = modeentry
        payment.customerid = customerid
        payment.rel_manager = rel_manager
        payment.broker = broker
        payment.nature = nature
        payment.remarks = remarks
        payment.underwriter = underwriter
        payment.ticket = ticket
        payment.status = status
        payment.voucher = voucher
        payment.history = history
        payment.completed = completed
        payment.proposal = proposal
        payment.policyno = policyno
        payment.instrumentno = instrumentno

        # db.session.add(payment)
        db.session.commit()
        return redirect(url_for("payment_page", payment_key=payment.id))

    form.customer.data = payment.customer

    # form.date.data = datetime.strptime(payment.date, "%Y-%m-%d") if payment.date else ""
    form.date.data = payment.date or ""
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

    brokers_list = [
        "Marsh",
        "Stenhouse",
        "BharatRe",
        "Willis Tower Watson",
        "Zeal",
        "JB Boda",
        "WAI",
        "Aum",
        "Prudent",
        "Ace",
        "Howden",
        "Pioneer",
        "Paavana",
        "Vision",
        "KM Dastur",
        "Aon",
        "TT Insurance",
        "Global",
        "First",
        "Unilight",
        "Optimum",
        "Welltech",
        "Premium",
        "Aditya Birla",
        "Equirus",
        "Securisk",
        "Heritage",
        "Ntrust",
        "Tata Motors",
        "Way2wealth",
        "Alliance",
        "Aims",
        "RMS ARC",
        "ANIB ESSEL",
        "Link-K",
        "Futurisk",
        "Profins",
        "India Insure",
        "Fouress",
    ]

    return render_template("payment_edit.html", form=form, brokers=brokers_list)


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
            # add employee number to employee database if employee number does not exist
            employee = Employee.query.filter(Employee.emp_number == emp_number).first()
            if not employee:
                print("employee number does not exist")
                new_employee = Employee(name=username, emp_number=emp_number)
                db.session.add(new_employee)
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

                next_page = request.args.get("next", url_for("home"))
                return redirect(next_page)
            else:
                flash("Invalid credentials.")
        else:
            flash("Invalid credentials.")
    return render_template("login.html", form=form)


def logout_page():
    logout_user()
    # flash("You have logged out.")
    return redirect(url_for("home"))
