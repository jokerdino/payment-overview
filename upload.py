import os

from server import create_app
from sqlite_excel import convert_input, export_database

app = create_app()
# db.init_app(app)
app.app_context().push()
# db.create_all()

export_database()

neft_incoming = r"D:\Downloads\MobileNeftPaymentDetailsReport.xls"

convert_input(neft_incoming)

os.remove(r"D:\Downloads\MobileNeftPaymentDetailsReport.xls")
