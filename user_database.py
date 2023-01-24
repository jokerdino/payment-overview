import sqlite3 as dbapi2

from user import User

class UserDatabase:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        
        

    def add_user(self, user):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT OR IGNORE INTO USER (USERNAME, PASSWORD) VALUES (?,?)"
            cursor.execute(query, (user.username, user.password))
            connection.commit()
            user_key = cursor.lastrowid
        return user_key
        
        
    def get_user(self, username):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT USERNAME, PASSWORD FROM USER WHERE (USERNAME = ?)"
            cursor.execute(query, (username,))
            username, password = cursor.fetchone()
        user_ = User(username, password = password)
        return user_
