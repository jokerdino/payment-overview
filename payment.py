class Payment:
    def __init__(self, customer, date=None, amount=None,
            mode=None, modeentry=None,rel_manager=None,
            broker=None,nature =None, remarks=None,underwriter=None,
            status=None,ticket=None):
        self.customer = customer
        self.date = date
        self.amount = amount
        self.mode = mode
        self.modeentry=modeentry
        self.rel_manager = rel_manager
        self.remarks = remarks
        self.underwriter = underwriter
        self.status = status
        self.ticket = ticket
        self.nature = nature
        self.broker = broker

