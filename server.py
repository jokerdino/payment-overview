import platform

from flask import Flask
from flask_login import LoginManager
from waitress import serve

import leave_views
import views
from database import Database
from employees import db
from user import get_user
from user_database import UserDatabase

lm = LoginManager()


@lm.user_loader
def load_user(username):
    return get_user(username)


def create_app():

    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/favicon.ico", view_func=views.favicon)
    app.add_url_rule("/signup", view_func=views.signup, methods=["GET", "POST"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/download", view_func=views.download, methods=["GET", "POST"])
    app.add_url_rule("/upload", view_func=views.upload, methods=["GET", "POST"])
    app.add_url_rule("/all", view_func=views.payments_all, methods=["GET", "POST"])
    app.add_url_rule("/cd_list", view_func=views.cd_list, methods=["GET"])
    app.add_url_rule(
        "/pending_scroll", view_func=views.pending_scroll_list, methods=["GET"]
    )
    app.add_url_rule(
        "/payments_pending_uw",
        view_func=views.payments_pending_uw,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/payments_completed",
        view_func=views.payments_completed,
        methods=["GET", "POST"],
    )
    app.add_url_rule("/payments/<int:payment_key>", view_func=views.payment_page)
    app.add_url_rule(
        "/new-payment", view_func=views.payment_add_page, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/payments/<int:payment_key>/edit",
        view_func=views.payment_edit_page,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/payments", view_func=views.payments_page, methods=["GET", "POST"]
    )
    app.add_url_rule(
        "/leave_management",
        view_func=leave_views.leave_project,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/leave_management/create_employee",
        view_func=leave_views.create_employee,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/leave_management/show_all",
        view_func=leave_views.show_all_employees,
        methods=["GET"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>",
        view_func=leave_views.employee_page,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/casual_leave",
        view_func=leave_views.add_casual_leave,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/sick_leave",
        view_func=leave_views.add_sick_leave,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/rh_leave",
        view_func=leave_views.add_rh_leave,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/lop_leave",
        view_func=leave_views.add_lop_leave,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/special_leave",
        view_func=leave_views.add_special_leave,
        methods=["GET", "POST"],
    )

    lm.init_app(app)
    lm.login_view = "login_page"

    if platform.system() == "Windows":
        db = Database(r"D:\payment-board\payments.sqlite")
        user_db = UserDatabase("D:\\payment-board\\user.sqlite")
    else:
        db = Database("payments.sqlite")
        user_db = UserDatabase("user.sqlite")
    app.config["db"] = db
    app.config["user_db"] = user_db

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///employees.sqlite"

    #    db.init_app(app)
    # import employees

    return app


if __name__ == "__main__":
    app = create_app()
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # db.drop_all()
    serve(app, host="0.0.0.0", port=8080)
