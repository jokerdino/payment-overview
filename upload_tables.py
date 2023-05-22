import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://barneedhar:barneedhar@localhost:5432/payments")

df_payments = pd.read_csv("backup_payments.csv")
df_payments.drop("id", inplace=True, axis=1)
df_user = pd.read_csv("backup_user.csv")
df_user.drop("id", inplace=True, axis=1)
df_employee = pd.read_csv("backup_employee.csv")
df_employee.drop("id", inplace=True, axis=1)
df_leaves = pd.read_csv("backup_leaves.csv")
df_leaves.drop("id", inplace=True, axis=1)

df_leaves["leave_letter_status"] = df_leaves["leave_letter_status"].astype(bool)
df_payments.to_sql("payment", engine, if_exists="append", index=False)
df_employee.to_sql("employee", engine, if_exists="append", index=False)
df_leaves.to_sql("leaves", engine, if_exists="append", index=False)


df_user["is_admin"] = df_user["is_admin"].astype(bool)
df_user["reset_password_page"] = df_user["reset_password_page"].astype(bool)
df_new = df_user.loc[~df_user.emp_number.isin(df_employee.emp_number)]
df_new["name"] = df_new["emp_number"]

df_new_stuff = df_new[["name", "emp_number"]]

df_new_stuff.to_sql("employee", engine, if_exists="append", index=False)


df_user.to_sql("user", engine, if_exists="append", index=False)
