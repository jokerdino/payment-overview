class Payment:
    def __init__(self, customer, date=None, amount=None,
            mode=None, modeentry=None, customerid = None, rel_manager=None,
            broker=None,nature =None, remarks=None,underwriter=None,
            ticket=None,status=None,voucher=None,created=None,history=None, completed=None):
        self.customer = customer
        self.date = date
        self.amount = amount
        self.mode = mode
        self.modeentry=modeentry
        self.customerid = customerid
        self.rel_manager = rel_manager
        self.remarks = remarks
        self.underwriter = underwriter
        self.ticket = ticket
        self.status = status
        self.nature = nature
        self.broker = broker
        self.voucher = voucher
        self.created = created
        self.history = history
        self.completed = completed
