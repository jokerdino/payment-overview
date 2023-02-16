# import platform

from flask import Flask
from flask_login import LoginManager
from waitress import serve

import leave_views
import user_views
import views

# from database import Database
from model import User, db

# from user_database import UserDatabase

lm = LoginManager()


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():

    app = Flask(__name__)
    app.config.from_object("settings")

    app.jinja_env.filters["dec_to_proper_frac"] = leave_views.dec_to_proper_frac

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
        methods=["GET", "POST"],
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

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/earned_leave",
        view_func=leave_views.add_earned_leave,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/calc_earned_leave",
        view_func=leave_views.calc_earned_leave_page,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/leave_encashment",
        view_func=leave_views.add_leave_encashment,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/leave_management/reports",
        view_func=leave_views.reports,
        methods=["GET"],
    )
    app.add_url_rule(
        "/leave_management/reports/lop",
        view_func=leave_views.reports_lop,
        methods=["GET"],
    )

    app.add_url_rule(
        "/leave_management/reports/strike",
        view_func=leave_views.reports_strike,
        methods=["GET"],
    )

    app.add_url_rule(
        "/leave_management/reports/sick_leave_half_pay",
        view_func=leave_views.reports_leave_sick_half_pay,
        methods=["GET"],
    )

    app.add_url_rule(
        "/leave_management/reports/leave_encashment",
        view_func=leave_views.reports_leave_encashment,
        methods=["GET"],
    )

    app.add_url_rule(
        "/leave_management/reports/leave_date",
        view_func=leave_views.reports_leave_on_specific_date,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/leaves_taken",
        view_func=leave_views.reports_leaves,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/leave_management/employee/<int:emp_key>/leave_letter_status",
        view_func=leave_views.reports_leave_letter,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/leave_management/restricted_holiday",
        view_func=leave_views.rh_list,
        methods=["GET"],
    )
    app.add_url_rule(
        "/leave_management/public_holiday",
        view_func=leave_views.public_holiday_list,
        methods=["GET"],
    )
    app.add_url_rule(
        "/user",
        view_func=user_views.view_all_users,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/user/<int:user_key>",
        view_func=user_views.view_user_page,
        methods=["GET", "POST"],
    )

    app.add_url_rule(
        "/user/reset_password",
        view_func=user_views.reset_password_page,
        methods=["GET", "POST"],
    )

    lm.init_app(app)
    lm.login_view = "login_page"

    #  if platform.system() == "Windows":
    #        db = Database(r"D:\payment-board\payments.sqlite")
    #    user_db = UserDatabase("D:\\payment-board\\user.sqlite")
    # else:
    #       db = Database("payments.sqlite")
    #   user_db = UserDatabase("user.sqlite")
    #  app.config["db"] = db
    # app.config["user_db"] = user_db

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///employees.sqlite"

    #    db.init_app(app)
    # import employees

    return app


if __name__ == "__main__":
    app = create_app()
    db.init_app(app)
    # migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()
        # db.drop_all()
    #        user_views.admin_check()
    serve(app, host="0.0.0.0", port=8080)
