import sqlite3 as dbapi2

from payment import Payment

class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile

    def add_payment(self, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO PAYMENT (CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, RM, BROKER, TYPE, REMARKS, UW, STATUS, TICKET) VALUES (?, ?,?,?,?,?,?,?,?,?,?,?)"
            cursor.execute(query, (payment.customer, payment.date, payment.amount,
                payment.mode, payment.modeentry, payment.rel_manager, payment.broker,
                payment.nature, payment.remarks, payment.underwriter, payment.status,
                payment.ticket))
            connection.commit()
            payment_key = cursor.lastrowid
        return payment_key

    def update_payment(self, payment_key, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE PAYMENT SET CUSTOMER = ?, DATE = ?, AMOUNT = ?, MODE = ?, MODEENTRY = ?, RM = ?, BROKER = ?, TYPE = ?, REMARKS = ?,UW = ?, STATUS = ?, TICKET = ?  WHERE (ID = ?)"
            cursor.execute(query, (payment.customer, payment.date, payment.amount,
                payment.mode, payment.modeentry, payment.rel_manager, payment.broker, payment.nature,
                payment.remarks, payment.underwriter, payment.status,
                payment.ticket, payment_key))
            connection.commit()

    def delete_payment(self, payment_key):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM PAYMENT WHERE (ID = ?)"
            cursor.execute(query, (payment_key,))
            connection.commit()

    def get_payment(self, payment_key):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, RM, BROKER, TYPE, REMARKS, UW, STATUS, TICKET FROM PAYMENT WHERE (ID = ?)"
            cursor.execute(query, (payment_key,))
            customer, date, amount, mode, modeentry, rel_manager, broker, nature, remarks, underwriter, status, ticket = cursor.fetchone()
        payment_ = Payment(customer, date=date, amount=amount, mode = mode, rel_manager = rel_manager,
                remarks = remarks, underwriter = underwriter, status = status,
                ticket = ticket, nature = nature,
                broker = broker, modeentry = modeentry)
        return payment_

    def get_payments(self):
        payments = []
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT ID, CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, RM, BROKER, TYPE, REMARKS, UW, STATUS,TICKET FROM PAYMENT ORDER BY ID"

            cursor.execute(query)
            for payment_key, customer, date, amount, mode, modeentry,rel_manager,broker,nature,remarks,underwriter,status,ticket in cursor:
                payments.append((payment_key, Payment(customer, date, amount, mode, modeentry, rel_manager, broker, nature, remarks,underwriter,status,ticket)))
        return payments
