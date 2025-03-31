import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

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
    user TEXT,
    board TEXT,
    type TEXT
)
""")
conn.commit()

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
    c.execute("INSERT INTO expenses (date, description, category, amount, currency, user, board, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (date, description, category, amount, currency, user, board, type_))
    conn.commit()
    st.success("Entry added successfully!")

# View and export data
st.header("View and Export Data")
df = pd.read_sql_query("SELECT * FROM expenses", conn)

if not df.empty:
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="expenses.csv")

st.header("Dashboard")
if not df.empty:
    income = df[df['type'] == "Income"]['amount'].sum()
    expense = df[df['type'] == "Expense"]['amount'].sum()
    net = income - expense

    st.metric("Total Income", f"{income:.2f} {currency}")
    st.metric("Total Expense", f"{expense:.2f} {currency}")
    st.metric("Net Total", f"{net:.2f} {currency}")
else:
    st.write("No data to display.")

conn.close()
