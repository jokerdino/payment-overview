from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

import pandas as pd
from datetime import datetime
import requests
import telegram_secrets

def export_database():
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

    return df_db_fetch

def convert_input(upload_file):
    # convert file downloaded from NEFT portal to required format
    df_db_fetch = export_database()

    df_db_fetch = df_db_fetch[df_db_fetch['STATUS'] == "To be receipted"]
    df_db = df_db_fetch.add_suffix('_db')

    my_path = "payments.sqlite"
    my_conn = create_engine("sqlite:///"+my_path)

    neft_incoming = pd.read_excel(upload_file,skiprows=4,usecols=range(1,16))
    neft_incoming = neft_incoming[neft_incoming['File Splited'] != "Yes"]
    neft_incoming = neft_incoming[neft_incoming['Download Status'] != "Downloaded"]

    neft_incoming['Reference Date'] = pd.to_datetime(neft_incoming['Reference Date'],dayfirst=True)

    # merge NEFT file with database csv file

    neft_incoming_merge =  neft_incoming.merge(df_db,right_on=('CUSTOMER_db','AMOUNT_db'),left_on=('Payee Name', 'Amount'), how='outer')
    neft_incoming_to_be_uploaded = neft_incoming_merge[neft_incoming_merge['CUSTOMER_db'].isna()]

    # create new dataframe with required column name and copy values from neft file to this format
    columns_list = df_db_fetch.columns.values
    empty_csv = pd.DataFrame(columns=[columns_list])
    empty_csv['CUSTOMER'] = neft_incoming_to_be_uploaded['Payee Name']
    empty_csv['AMOUNT'] = neft_incoming_to_be_uploaded['Amount']
    empty_csv['DATE'] = neft_incoming_to_be_uploaded['Reference Date']
    empty_csv['INSTRUMENTNO'] = neft_incoming_to_be_uploaded['Reference No']
    empty_csv['MODE'] = "NEFT"
    empty_csv['STATUS'] = "To be receipted"
    empty_csv['CREATED'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    file_name = "upload"+datetime.now().strftime("%d%m%Y %H%M%S") + ".csv"

    try:
        empty_csv['HISTORY'] = empty_csv[['CREATED', 'STATUS']].agg(": ".join,axis=1)
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
            CHAT_ID = telegram_secrets.CHAT_ID
            SEND_URL = telegram_secrets.SEND_URL
#            df_upload.to_excel("file.xlsx",index=False)
            for i in range(len(df_upload)):
                title = df_upload.iloc[i,0]
                string_date = df_upload.iloc[i,1]
                mode = df_upload.iloc[i,3]
                amount = df_upload.iloc[i,2]
                instrumentno = df_upload.iloc[i,19]
                message = ("""Payee name: %s
                Amount received: %s
                Date of payment: %s
                Mode of payment: %s
                Instrument number: %s
                """ % (title, amount, string_date, mode, instrumentno))


                requests.post(SEND_URL, json={'chat_id': CHAT_ID, 'text': message})
            print("Uploaded successfully.")
    except ValueError as e:
        print("All pending transactions have already been uploaded to database.")

