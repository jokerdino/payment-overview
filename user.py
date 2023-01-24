from flask import current_app
from flask_login import UserMixin




class User(UserMixin):

    def __init__(self, username, password, is_admin):
        #self.name = name
        self.username = username
        self.password = password
        self.active = True

        self.is_admin = False
        #self.is_superadmin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active

def get_user(username):
    user_db = current_app.config["user_db"]
    user = user_db.get_user(username)
   # password = current_app.config["PASSWORDS"].get(user_id)
    #user = User(user_id, password) if password else None
    if user is not None:
        #user.is_admin
        #if user.admin > 0 :
         #   user.is_admin
        user.is_admin = user.username in current_app.config["ADMIN_USERS"]
      #  user.is_superadmin = user.username in current_app.config["SUPERADMIN"]
    return user
