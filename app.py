import streamlit as st
import pandas as pd
import sqlite3
import requests
import os
from datetime import datetime

# Get the API key from environment variables
currency_api_key = os.getenv("CURRENCY_API_KEY")

# Set up database connection
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# Create the expenses table if not exists
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    description TEXT,
    category TEXT,
    amount REAL,
    currency TEXT,
    amount_crc REAL,
    user TEXT,
    board TEXT,
    type TEXT
)
""")
conn.commit()

# Currency conversion function
def convert_to_crc(amount, currency):
    if currency == "CRC":
        return amount
    url = f"https://open.er-api.com/v6/latest/{currency}"
    try:
        response = requests.get(url)
        data = response.json()
        rate = data["rates"].get("CRC", 1)
        return round(amount * rate, 2)  # Format to 2 decimal places
    except:
        return amount

# Title
st.title("Financial Dashboard")

# User input form
st.header("Add New Entry")
date = st.date_input("Date", datetime.today())
description = st.text_input("Description")
category = st.selectbox("Category", ["Groceries", "Rent", "Utilities", "Personal", "Dividends", "Operational", "Other"])
amount = st.number_input("Amount", min_value=0.0, format="%f")
currency = st.selectbox("Currency", ["CRC", "USD", "EUR"])
user = st.selectbox("User", ["Javi", "Rima", "Carmen", "Nelson", "David"])
board = st.selectbox("Board", ["Personal", "Custom 1", "Custom 2", "Custom 3", "Custom 4", "Bombastic"])
type_ = st.selectbox("Type", ["Income", "Expense"])

if st.button("Add Entry"):
    amount_crc = convert_to_crc(amount, currency)
    c.execute("INSERT INTO expenses (date, description, category, amount, currency, amount_crc, user, board, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (date, description, category, amount, currency, amount_crc, user, board, type_))
    conn.commit()
    st.success("Entry added successfully!")

# View and export data
st.header("View and Export Data")
df = pd.read_sql_query("SELECT * FROM expenses", conn)

if not df.empty:
    df['amount_crc'] = df['amount_crc'].map("{:,.2f}".format)  # Format CRC amount
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="expenses.csv")

st.header("Dashboard")
if not df.empty:
    income = df[df['type'] == "Income"]['amount_crc'].astype(float).sum()
    expense = df[df['type'] == "Expense"]['amount_crc'].astype(float).sum()
    net = income - expense

    st.metric("Total Income (CRC)", f"{income:,.2f} CRC")
    st.metric("Total Expense (CRC)", f"{expense:,.2f} CRC")
    st.metric("Net Total (CRC)", f"{net:,.2f} CRC")
else:
    st.write("No data to display.")

conn.close()
