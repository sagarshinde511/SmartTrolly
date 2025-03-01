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

# Streamlit UI
st.title("🛒 Smart Trolly System")

# Create tabs
tab1, tab2 = st.tabs(["Trolly Products", "Trolly Carts"])

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

    # Fetch order data
    df_orders = fetch_data("TrollyOrder")
    
    if not df_orders.empty:
        # Standardize column names (remove spaces and lowercase)
        df_orders.columns = df_orders.columns.str.strip().str.lower()

        # Ensure correct column names
        expected_columns = ["rfidno", "name", "weight", "price"]
        df_orders = df_orders[[col for col in expected_columns if col in df_orders.columns]]

        # Convert price to float
        df_orders["price"] = pd.to_numeric(df_orders["price"], errors="coerce").fillna(0)

        # Add Delete button in a new column
        df_orders["action"] = df_orders["rfidno"].apply(lambda x: f"🗑️ Delete {x}")

        # Display order table
        edited_df = st.data_editor(
            df_orders[["rfidno", "name", "weight", "price", "action"]],
            column_config={"action": st.column_config.TextColumn("Action")},
            hide_index=True
        )

        # Create delete buttons for each row
        for rfid_no in df_orders["rfidno"]:
            if st.button(f"Delete {rfid_no}"):
                delete_row(rfid_no)
                st.success(f"Deleted item with RFidNo: {rfid_no}")
                st.experimental_rerun()

        # Calculate and display total bill
        total_bill = df_orders["price"].sum()
        st.subheader(f"💰 Total Bill: ₹{total_bill}")

    else:
        st.warning("No items in the cart.")
