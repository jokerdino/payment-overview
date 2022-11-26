from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

import pandas as pd
from datetime import datetime

# build connection to database
my_path = "payments.sqlite"
my_conn = create_engine("sqlite:///"+my_path)

# export from database to csv
try:
    query = "SELECT * FROM PAYMENT"
    df_db_fetch = pd.read_sql(query, my_conn, index_col='ID')
except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)
else:
    print("File created successfully.")


# add suffix to database csv file
df_db_fetch = df_db_fetch[df_db_fetch['STATUS'] == "To be receipted"]
df_db = df_db_fetch.add_suffix('_db')

# convert file downloaded from NEFT portal to required format
neft_incoming = pd.read_excel('MobileNeftPaymentDetailsReport.xls',skiprows=4,usecols=range(1,16))
neft_incoming = neft_incoming[neft_incoming['File Splited'] != "Yes"]
neft_incoming = neft_incoming[neft_incoming['Download Status'] != "Downloaded"]

neft_incoming['Reference Date'] = pd.to_datetime(neft_incoming['Reference Date'],infer_datetime_format=True)

# merge NEFT file with database csv file

neft_incoming_merge =  neft_incoming.merge(df_db,right_on=('CUSTOMER_db','AMOUNT_db'),left_on=('Payee Name', 'Amount'), how='outer')
neft_incoming_to_be_uploaded = neft_incoming_merge[neft_incoming_merge['CUSTOMER_db'].isna()]

# create new dataframe with required column name and copy values from neft file to this format
columns_list = df_db_fetch.columns.values
empty_csv = pd.DataFrame(columns=[columns_list])
empty_csv['CUSTOMER'] = neft_incoming_to_be_uploaded['Payee Name']
empty_csv['AMOUNT'] = neft_incoming_to_be_uploaded['Amount']
empty_csv['DATE'] = neft_incoming_to_be_uploaded['Reference Date']#.strftime("%Y-%m-%d")
empty_csv['MODE'] = "NEFT"
empty_csv['STATUS'] = "To be receipted"
empty_csv['CREATED'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

file_name = datetime.now().strftime("%d%m%Y %H%M%S") + ".csv"

try:
    empty_csv['HISTORY'] = empty_csv[['STATUS', 'CREATED']].agg(": ".join,axis=1)
    empty_csv.to_csv(file_name,index=False)

    # upload prepared csv file to database
    try:
        df_upload = pd.read_csv(file_name)
        df_upload.to_sql(con=my_conn,name='PAYMENT',if_exists='append',index=False)

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        print(error)
    else:
        print(df_upload)
        print("Uploaded successfully.")
except ValueError as e:
    print("All pending transactions have already been uploaded to database.")

