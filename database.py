import sqlite3 as dbapi2

from payment import Payment

class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile

    def add_payment(self, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO PAYMENT (TITLE, DATE) VALUES (?, ?)"
            cursor.execute(query, (payment.customer, payment.date))
            connection.commit()
            payment_key = cursor.lastrowid
        return payment_key

    def update_payment(self, payment_key, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE PAYMENT SET TITLE = ?, DATE = ? WHERE (ID = ?)"
            cursor.execute(query, (payment.customer, payment.date, payment_key))
            connection.commit()

    def delete_payment(self, payment_key):
        if payment_key in self.payments:
            del self.payments[payment_key]

    def get_payment(self, payment_key):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT TITLE, DATE FROM PAYMENT WHERE (ID = ?)"
            cursor.execute(query, (payment_key,))
            customer, date = cursor.fetchone()
        payment_ = Payment(customer, date=date)
        return payment_

    def get_payments(self):
        payments = []
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT ID, TITLE, DATE FROM PAYMENT ORDER BY ID"
            cursor.execute(query)
            for payment_key, customer, date in cursor:
                payments.append((payment_key, Payment(customer, date)))
        return payments
