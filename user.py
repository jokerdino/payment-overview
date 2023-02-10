from flask import current_app
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password, emp_number):
        self.username = username
        self.password = password
        self.emp_number = emp_number
        self.active = True

        self.is_admin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(username):
    user_db = current_app.config["user_db"]
    user = user_db.get_user(username)
    if user is not None:
        user.is_admin = user.username in current_app.config["ADMIN_USERS"]
    return user
