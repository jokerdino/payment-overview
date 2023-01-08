import pandas as pd
import xlsxwriter

file = pd.read_excel('MobileNeftPaymentDetailsReport.xls', skiprows=4,usecols=range(1,16))

file = file[file['File Splited'] != "Yes"]
file = file[file['Download Status'] != "Downloaded"]


file = file[["Reference No","Reference Date","Payee Name","Amount"]]

file.loc["Total", "Amount"] = file.Amount.sum()
file["Customer ID"] = ""


file.to_excel("Premium to be receipted.xlsx",index=None)


writer = pd.ExcelWriter("Premium to be receipted.xlsx", engine = 'xlsxwriter')

file.to_excel(writer, index=None,sheet_name='Sheet1')

workbook = writer.book
worksheet = writer.sheets['Sheet1']

format_currency = workbook.add_format({
    "num_format":"##,##,#0","bold":False
    })

worksheet.set_column("D:D",12,format_currency)

writer.save()

