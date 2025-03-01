import mysql.connector
import pandas as pd
import streamlit as st

# MySQL database connection details
host = "82.180.143.66"
user = "u263681140_students1"
password = "testStudents@123"
database = "u263681140_students1"

# Function to fetch data from a table
def fetch_data(table_name):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        if connection.is_connected():
            cursor = connection.cursor()
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            cursor.close()
            connection.close()
            return pd.DataFrame(records, columns=columns)
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return pd.DataFrame()

# Function to delete a row from the table
def delete_row(table_name, column_name, value):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        if connection.is_connected():
            cursor = connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {column_name} = %s"
            cursor.execute(query, (value,))
            connection.commit()
            cursor.close()
            connection.close()
            st.success(f"Deleted row with {column_name} = {value} successfully!")
    except mysql.connector.Error as e:
        st.error(f"Error deleting row: {e}")

# Streamlit UI
st.title("Trolly Carts Data Viewer")

# Create tabs for separate tables
tab1, tab2 = st.tabs(["TrollyProducts", "TrollyOrder"])

# Tab 1: Display TrollyProducts Table
with tab1:
    st.subheader("TrollyProducts Table")
    data_products = fetch_data("TrollyProducts")
    if not data_products.empty:
        st.dataframe(data_products)
    else:
        st.warning("No data found in TrollyProducts table.")

# Tab 2: Display TrollyOrder Table with Delete Option
with tab2:
    st.subheader("TrollyOrder Table")
    data_order = fetch_data("TrollyOrder")

    if not data_order.empty:
        # Convert 'price' column to numeric and calculate total bill
        try:
            data_order["price"] = pd.to_numeric(data_order["price"], errors="coerce")
            total_bill = data_order["price"].sum()
            st.success(f"**Total Bill: ₹{total_bill:.2f}**")
        except Exception as e:
            st.error(f"Error calculating total bill: {e}")

        # Create a delete button for each row
        selected_index = st.selectbox("Select a row to delete", data_order.index)
        selected_row = data_order.iloc[selected_index]

        if st.button(f"Delete Row {selected_index}"):
            delete_row("TrollyOrder", "RFidNo", selected_row["RFidNo"])  # Assuming RFidNo is the unique identifier
            st.experimental_rerun()  # Refresh the table after deletion

    else:
        st.warning("No data found in TrollyOrder table.")
