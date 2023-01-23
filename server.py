import os.path
import platform

from flask import Flask, render_template
from flask_login import LoginManager

from waitress import serve
#from gevent.pywsgi import WSGIServer

import views
from database import Database
from payment import Payment
from user import get_user


lm = LoginManager()

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)



def create_app():


    app = Flask(__name__)
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/favicon.ico",view_func=views.favicon)
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET","POST"])
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/download",view_func=views.download,methods=["GET","POST"])
    app.add_url_rule("/upload",view_func=views.upload,methods=["GET","POST"])
    app.add_url_rule("/all",view_func=views.payments_all,methods=["GET"])
    app.add_url_rule("/cd_list",view_func=views.cd_list,methods=['GET'])
    app.add_url_rule("/pending_scroll",view_func=views.pending_scroll_list,methods=['GET'])
    app.add_url_rule("/payments_pending_uw", view_func=views.payments_pending_uw,methods=["GET","POST"])
    app.add_url_rule("/payments_completed", view_func=views.payments_completed,methods=["GET","POST"])
    app.add_url_rule("/payments/<int:payment_key>",view_func=views.payment_page)
    app.add_url_rule("/new-payment", view_func=views.payment_add_page,methods=["GET","POST"])
    app.add_url_rule("/payments/<int:payment_key>/edit",view_func=views.payment_edit_page,
            methods=["GET","POST"],)
    app.add_url_rule("/payments",view_func=views.payments_page, methods=["GET","POST"])

    lm.init_app(app)
    lm.login_view = "login_page"

    home_dir = os.path.expanduser("~")
    if platform.system() == "Windows":
        db = Database("D:\payment-board\payments.sqlite")
    else:
        db = Database("payments.sqlite")
    app.config["db"] = db

#    app.config["DEBUG"] = True
    return app


if __name__ == "__main__":
    app = create_app()
  #  http_server = WSGIServer(("0.0.0.0", 8080), app)
  #  http_server.serve_forever()
 #   app.run(host="0.0.0.0", port=8080)
    serve(app, host="0.0.0.0", port=8080)
#

