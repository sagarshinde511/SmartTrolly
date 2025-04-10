import streamlit as st
import pandas as pd
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students1",
        password="testStudents@123",
        database="u263681140_students1"
    )

def fetch_data(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data) if data else pd.DataFrame()

def delete_row(rfid_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TrollyOrder WHERE RFidNo = %s", (rfid_no,))
    conn.commit()
    conn.close()

def insert_product(rfid, name, group, weight, price):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TrollyProducts (RFid, Name, `Group`, Weight, Price) VALUES (%s, %s, %s, %s, %s)",
                       (rfid, name, group, weight, price))
        conn.commit()
        conn.close()
        return True
    except mysql.connector.Error as e:
        return False

def fetch_dropdown_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, `Group` FROM TrollyProductsDropDown")
    data = cursor.fetchall()
    conn.close()
    name_list = [row[0] for row in data]
    group_list = [row[1] for row in data]
    return name_list, group_list

def insert_dropdown_product(name, group):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TrollyProductsDropDown (Name, `Group`) VALUES (%s, %s)", (name, group))
        conn.commit()
        conn.close()
        return True
    except mysql.connector.Error as e:
        return False

def fetch_stock_data(name_filter=None, weight_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT Name, Weight, COUNT(*) as Stock FROM TrollyProducts"
    conditions = []
    params = []
    
    if name_filter:
        conditions.append("Name = %s")
        params.append(name_filter)
    if weight_filter:
        conditions.append("Weight = %s")
        params.append(weight_filter)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY Name, Weight"
    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data) if data else pd.DataFrame()

# Streamlit UI
st.title("🛒 Smart Trolly System")

# Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.session_state.logged_in = True
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.rerun()

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
    tab1, tab2, tab3, tab4 = st.tabs(["Trolly Carts", "Trolly Products", "Register Product", "Stock Data"])
    
    with tab1:
        st.subheader("🛒 Your Cart")
        df_orders = fetch_data("TrollyOrder")
        if not df_orders.empty:
            df_orders.columns = df_orders.columns.str.strip().str.lower()
            expected_columns = ["rfidno", "name", "weight", "price"]
            df_orders = df_orders[[col for col in expected_columns if col in df_orders.columns]]
            df_orders["price"] = pd.to_numeric(df_orders["price"], errors="coerce").fillna(0)
            df_orders["action"] = df_orders["rfidno"].apply(lambda x: f"🗑️ Delete {x}")
            edited_df = st.data_editor(
                df_orders[["rfidno", "name", "weight", "price", "action"]],
                column_config={"action": st.column_config.TextColumn("Action")},
                hide_index=True
            )
            for rfid_no in df_orders["rfidno"]:
                if st.button(f"Delete {rfid_no}"):
                    delete_row(rfid_no)
                    st.success(f"Deleted item with RFidNo: {rfid_no}")
                    st.rerun()
            st.subheader(f"💰 Total Bill: ₹{df_orders['price'].sum()}")
        else:
            st.warning("No items in the cart.")
    
    with tab2:
        st.subheader("📦 Available Products")
        df_products = fetch_data("TrollyProducts")
        if not df_products.empty:
            st.dataframe(df_products)
        else:
            st.warning("No products available.")
    
    with tab3:
        st.subheader("➕ Register New Product")
        option = st.radio("Choose an option:", ["Register Product", "Add Drop-down Product"])
        if option == "Register Product":
            rfid = st.text_input("RFID Number")
            name_options, group_options = fetch_dropdown_options()
            name = st.selectbox("Product Name", name_options)
            group = st.selectbox("Product Group", group_options)
            weight = st.number_input("Weight (in grams)", min_value=0.0, format="%.2f")
            price = st.number_input("Price (in ₹)", min_value=0.0, format="%.2f")
            if st.button("Register Product"):
                if rfid and name and group and weight > 0 and price > 0:
                    if insert_product(rfid, name, group, weight, price):
                        st.success("✅ Product registered successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ Error: Could not insert the product.")
                else:
                    st.error("⚠️ Please fill in all details correctly.")
    
    with tab4:
        st.subheader("📊 Stock Data")
        df_stock = fetch_stock_data()
        if not df_stock.empty:
            st.dataframe(df_stock)
        else:
            st.warning("No stock data available.")
