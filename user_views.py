from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from forms import ResetPasswordForm, UpdateUserForm
from model import User

# from server import db


def view_all_users():

    if request.method == "POST":
        # delete employee
        from server import db

        form_user_keys = request.form.getlist("user_keys")
        for form_user_key in form_user_keys:

            user = User.query.get_or_404(form_user_key)
            user.query.filter(User.id == form_user_key).delete()
            # Leaves.query.filter(Leaves.emp_number == employee.emp_number).delete()
            db.session.commit()
        return render_template("view_all_users.html", users=User.query.all())

    else:
        return render_template("view_all_users.html", users=User.query.all())
    # return render_template("view_all_users.html", users=User.query.all())


def view_user_page(user_key):
    user = User.query.get_or_404(user_key)
    form = UpdateUserForm()
    from server import db

    if request.method == "POST":

        is_admin = form.data["is_admin"]
        reset_password_page = form.data["reset_password_page"]

        user.is_admin = is_admin
        user.reset_password_page = reset_password_page
        db.session.add(user)
        db.session.commit()
        admin_check()
        return redirect(url_for("view_all_users"))

    form.is_admin.data = user.is_admin
    form.reset_password_page.data = user.reset_password_page

    return render_template("user_page.html", user=user, form=form)


def reset_password_page():
    #    pass
    form = ResetPasswordForm()
    from server import db

    #  form = SignupForm()
    if request.method == "GET":
        return render_template("reset_password.html", form=form)
    else:

        username = form.data["username"]
        emp_number = form.data["emp_number"]

        user = User.query.filter(
            User.username == username, User.emp_number == emp_number
        ).first()
        if user:
            if user.reset_password_page:
                password = form.data["password"]
                password_hash = generate_password_hash(password, method="sha256")
                user.password = password_hash
                user.reset_password_page = False
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login_page"))
            else:
                flash(
                    "Password reset page is not enabled for this user. Contact admin."
                )
            # return redirect(url_for("signup"))

        else:
            flash("Username or employee number does not exist.")
    return render_template("reset_password.html", form=form)


def admin_check():
    from server import db

    admin = db.session.query(User).filter(User.is_admin == 1).first()
    if not admin:
        user = db.session.query(User).first()
        if user:  # .query.first()
            user.is_admin = 1
            db.session.commit()
            print("user has been made admin")
