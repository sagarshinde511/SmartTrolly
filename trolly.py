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
    return data

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
    products_data = fetch_data("TrollyProducts")
    
    if products_data:
        df_products = pd.DataFrame(products_data)
        st.dataframe(df_products)
    else:
        st.write("No products available.")

# 🛒 **Tab 2: Display Trolly Carts (Orders)**
with tab2:
    st.subheader("🛒 Your Cart")

    # Fetch order data
    order_data = fetch_data("TrollyOrder")
    
    if order_data:
        df_orders = pd.DataFrame(order_data)

        # Add Delete button in a new column
        df_orders["Action"] = df_orders["RFidNo"].apply(lambda x: f"🗑️ Delete {x}")

        # Display order table
        edited_df = st.data_editor(
            df_orders[["RFidNo", "Name", "Weight", "Price", "Action"]],
            column_config={"Action": st.column_config.TextColumn("Action")},
            hide_index=True
        )

        # Create delete buttons for each row
        for rfid_no in df_orders["RFidNo"]:
            if st.button(f"Delete {rfid_no}"):
                delete_row(rfid_no)
                st.success(f"Deleted item with RFidNo: {rfid_no}")
                st.experimental_rerun()

        # Calculate and display total bill
        total_bill = df_orders["Price"].astype(float).sum()
        st.subheader(f"💰 Total Bill: ₹{total_bill}")

    else:
        st.write("No items in the cart.")
