from datetime import datetime

import pandas as pd
import requests
from sqlalchemy.exc import SQLAlchemyError

import telegram_secrets
from model import Payment


def export_database():
    # build connection to database
    from server import db

    #    df_db_fetch = pd.read_sql(
    #    db.session.query(Payment)
    #    #.filter(Leaves.emp_number == employee.emp_number)
    #    .statement,
    #    db.get_engine(),
    #    )
    #  my_path = "payments.sqlite"
    # my_conn = create_engine("sqlite:///" + my_path)
    # export from database to csv
    try:
        df_db_fetch = pd.read_sql(
            db.session.query(Payment)
            # .filter(Leaves.emp_number == employee.emp_number)
            .statement,
            db.get_engine(),
        )
        # query = "SELECT * FROM PAYMENT"
        # df_db_fetch = pd.read_sql(query, my_conn, index_col="ID")
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        print(error)
    else:
        df_db_fetch.to_csv("file1.csv")
        print("File created successfully.")

    # add suffix to database csv file

    return df_db_fetch


def convert_input(upload_file):
    from server import db

    # convert file downloaded from NEFT portal to required format
    df_db_fetch = export_database()

    df_db_fetch = df_db_fetch[df_db_fetch["status"] == "To be receipted"]
    df_db = df_db_fetch.add_suffix("_db")
    df_db.to_csv("db.csv")
    # my_path = "employees.sqlite"
    # my_conn = create_engine("sqlite:///" + my_path)

    neft_incoming = pd.read_excel(upload_file, skiprows=4, usecols=range(1, 16))
    neft_incoming = neft_incoming[neft_incoming["File Splited"] != "Yes"]
    neft_incoming = neft_incoming[neft_incoming["Download Status"] != "Downloaded"]
    df_db["amount_db"] = df_db["amount_db"]  # .astype(float)
    neft_incoming["Reference Date"] = pd.to_datetime(
        neft_incoming["Reference Date"], dayfirst=True
    )

    # merge NEFT file with database csv file

    neft_incoming_merge = neft_incoming.merge(
        df_db,
        right_on=("customer_db", "amount_db"),
        left_on=("Payee Name", "Amount"),
        how="outer",
    )
    neft_incoming_to_be_uploaded = neft_incoming_merge[
        neft_incoming_merge["customer_db"].isna()
    ]

    # create new dataframe with required column name and copy values from neft file to this format
    columns_list = df_db_fetch.columns.values
    empty_csv = pd.DataFrame(columns=[columns_list])
    empty_csv["customer"] = neft_incoming_to_be_uploaded["Payee Name"]
    empty_csv["amount"] = neft_incoming_to_be_uploaded["Amount"]
    empty_csv["date"] = neft_incoming_to_be_uploaded["Reference Date"]
    empty_csv["instrumentno"] = neft_incoming_to_be_uploaded["Reference No"]
    empty_csv["mode"] = "NEFT"
    empty_csv["status"] = "To be receipted"
    empty_csv["created"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    file_name = "upload" + datetime.now().strftime("%d%m%Y %H%M%S") + ".csv"

    try:
        empty_csv["history"] = empty_csv[["created", "status"]].agg(": ".join, axis=1)
        empty_csv.to_csv(file_name, index=False)

        # upload prepared csv file to database
        try:
            df_upload = pd.read_csv(file_name)
            df_upload.to_sql(
                con=db.get_engine(), name="payment", if_exists="append", index=False
            )

        except SQLAlchemyError as e:
            error = str(e.__dict__["orig"])
            print("test error")
            print(error)
        else:
            print(df_upload)
            CHAT_ID = telegram_secrets.CHAT_ID
            SEND_URL = telegram_secrets.SEND_URL
            #            df_upload.to_excel("file.xlsx",index=False)
            for i in range(len(df_upload)):
                title = df_upload.iloc[i, 0]
                received_date = df_upload.iloc[i, 1]
                date_received_date = datetime.strptime(received_date, "%Y-%m-%d")
                string_date = date_received_date.strftime("%d-%m-%Y")
                mode = df_upload.iloc[i, 3]
                amount = df_upload.iloc[i, 2]
                instrumentno = df_upload.iloc[i, 19]
                message = """Payee name: {}
Amount received: {}
Date of payment: {}
Mode of payment: {}
Instrument number: {}
                """.format(
                    title,
                    amount,
                    string_date,
                    mode,
                    instrumentno,
                )

                requests.post(SEND_URL, json={"chat_id": CHAT_ID, "text": message})
            print("Uploaded successfully.")
    except ValueError as e:
        print("All pending transactions have already been uploaded to database.")
