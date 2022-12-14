import sqlite3 as dbapi2

from payment import Payment

class Database:
    def __init__(self, dbfile):
        self.dbfile = dbfile

    def add_payment(self, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO PAYMENT (CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, CUSTOMERID, RM, BROKER, TYPE, REMARKS, UW, TICKET, STATUS, VOUCHER, CREATED, HISTORY, COMPLETED, PROPOSAL, POLICYNO) VALUES (?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            cursor.execute(query, (payment.customer, payment.date, payment.amount,
                payment.mode, payment.modeentry, payment.customerid, payment.rel_manager, payment.broker,
                payment.nature, payment.remarks, payment.underwriter, payment.ticket,
                payment.status, payment.voucher, payment.created, payment.history, payment.completed,
                payment.proposal, payment.policyno))
            connection.commit()
            payment_key = cursor.lastrowid
        return payment_key

    def update_payment(self, payment_key, payment):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE PAYMENT SET CUSTOMER = ?, DATE = ?, AMOUNT = ?, MODE = ?, MODEENTRY = ?, CUSTOMERID = ?, RM = ?, BROKER = ?, TYPE = ?, REMARKS = ?,UW = ?, TICKET = ?, STATUS = ?, VOUCHER = ?, HISTORY = ?, COMPLETED = ?, PROPOSAL = ?, POLICYNO = ? WHERE (ID = ?)"
            cursor.execute(query, (payment.customer, payment.date, payment.amount,
                payment.mode, payment.modeentry, payment.customerid, payment.rel_manager,
                payment.broker, payment.nature, payment.remarks,
                payment.underwriter, payment.ticket, payment.status, payment.voucher, payment.history, payment.completed, payment.proposal, payment.policyno, payment_key))
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
            query = "SELECT CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, CUSTOMERID, RM, BROKER, TYPE, REMARKS, UW, TICKET, STATUS, VOUCHER, CREATED, HISTORY, COMPLETED, PROPOSAL, POLICYNO FROM PAYMENT WHERE (ID = ?)"
            cursor.execute(query, (payment_key,))
            customer, date, amount, mode, modeentry, customerid, rel_manager, broker, nature, remarks, underwriter, ticket, status, voucher, created, history, completed, proposal, policyno = cursor.fetchone()
        payment_ = Payment(customer, date=date, amount=amount, mode = mode, customerid = customerid,
                rel_manager = rel_manager, remarks = remarks, underwriter = underwriter,
                status = status, ticket = ticket, nature = nature,
                broker = broker, modeentry = modeentry, voucher = voucher,
                created = created, history = history, completed = completed, proposal = proposal, policyno = policyno)
        return payment_

    def get_payments(self):
        payments = []
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT ID, CUSTOMER, DATE, AMOUNT, MODE, MODEENTRY, CUSTOMERID, RM, BROKER, TYPE, REMARKS, UW, TICKET, STATUS, VOUCHER, CREATED, HISTORY, COMPLETED, PROPOSAL, POLICYNO FROM PAYMENT ORDER BY ID"

            cursor.execute(query)
            for payment_key, customer, date, amount, mode, modeentry, customerid, rel_manager, broker, nature, remarks, underwriter, ticket, status, voucher, created, history, completed, proposal, policyno in cursor:
                payments.append((payment_key, Payment(customer, date, amount, mode, modeentry,
                    customerid, rel_manager, broker, nature, remarks,
                    underwriter, ticket, status, voucher, created, history, completed, proposal, policyno)))
        return payments
