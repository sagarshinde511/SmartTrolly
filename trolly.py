import streamlit as st
import pandas as pd
import mysql.connector

# Function to connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students1",
        password="testStudents@123",
        database="u263681140_students1"
    )

# Function to fetch data from a table
def fetch_data(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data) if data else pd.DataFrame()

# Function to delete a row based on RFidNo
def delete_row(rfid_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TrollyOrder WHERE RFidNo = %s", (rfid_no,))
    conn.commit()
    conn.close()

# Function to check if RFID already exists
def check_rfid_exists(rfid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TrollyProducts WHERE RFid = %s", (rfid,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
    
# Function to insert a new product (Allowing duplicate RFID values)
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
        print("Error:", e)
        return False  # Handle insertion errors gracefully

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

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Trolly Products", "Trolly Carts", "Register Product", "Stock Data"])

# 🛍️ **Tab 1: Display Trolly Products**
with tab1:
    st.subheader("📦 Available Products")
    df_products = fetch_data("TrollyProducts")
    
    if not df_products.empty:
        st.dataframe(df_products)
    else:
        st.warning("No products available.")

# 🛒 **Tab 2: Display Trolly Carts (Orders)**
with tab2:
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
                st.experimental_rerun()
        
        total_bill = df_orders["price"].sum()
        st.subheader(f"💰 Total Bill: ₹{total_bill}")
    else:
        st.warning("No items in the cart.")

# 🏷️ **Tab 3: Register New Product**
with tab3:
    st.subheader("➕ Register New Product")
    
    rfid = st.text_input("RFID Number")
    name_options = ["Apple", "Banana", "Milk", "Bread", "Eggs"]
    group_options = ["Fruits", "Dairy", "Bakery", "Grocery"]
    name = st.selectbox("Product Name", name_options)
    group = st.selectbox("Product Group", group_options)
    weight = st.number_input("Weight (in grams)", min_value=0.0, format="%.2f")
    price = st.number_input("Price (in ₹)", min_value=0.0, format="%.2f")
    
    if st.button("Register Product"):
        if rfid and name and group and weight > 0 and price > 0:
            if insert_product(rfid, name, group, weight, price):
                st.success("✅ Product registered successfully!")
                st.experimental_rerun()
            else:
                st.error("⚠️ Error: RFID already exists! Please use a different RFID.")
        else:
            st.error("⚠️ Please fill in all details correctly.")
# 📊 **Tab 4: Stock Data**
with tab4:
    st.subheader("📊 Stock Data")
    name_filter = st.text_input("Filter by Name")
    weight_filter = st.number_input("Filter by Weight", min_value=0.0, format="%.2f")
    df_stock = fetch_stock_data(name_filter if name_filter else None, weight_filter if weight_filter > 0 else None)
    
    if not df_stock.empty:
        st.dataframe(df_stock)
    else:
        st.warning("No stock data available.")
