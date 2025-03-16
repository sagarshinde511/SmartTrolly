import streamlit as st
import pandas as pd
import mysql.connector

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students1",
        password="testStudents@123",
        database="u263681140_students1"
    )

# Authentication logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.session_state.logged_in = True

def logout():
    st.session_state.logged_in = False

# **Login Page**
if not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            login()
        else:
            st.error("Invalid credentials!")
else:
    st.sidebar.button("Logout", on_click=logout)
    st.success("✅ Logged in successfully!")

    # **Main App Tabs**
    tab1, tab2, tab3, tab4 = st.tabs(["Trolly Carts", "Trolly Products", "Register Product", "Stock Data"])

    with tab1:
        st.subheader("🛒 Your Cart")
        df_orders = pd.DataFrame()  # Fetch from DB
        st.write(df_orders)

    with tab2:
        st.subheader("📦 Available Products")
        df_products = pd.DataFrame()  # Fetch from DB
        st.write(df_products)

    with tab3:
        st.subheader("➕ Register New Product")
        name = st.text_input("Product Name")
        if st.button("Register Product"):
            st.success("✅ Product registered!")

    with tab4:
        st.subheader("📊 Stock Data")
        df_stock = pd.DataFrame()  # Fetch from DB
        st.write(df_stock)
