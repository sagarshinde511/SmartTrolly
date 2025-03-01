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
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Query to fetch all data from the given table
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

            # Fetch column names
            columns = [desc[0] for desc in cursor.description]

            # Fetch all rows
            records = cursor.fetchall()

            # Convert to DataFrame
            df = pd.DataFrame(records, columns=columns)

            # Close cursor and connection
            cursor.close()
            connection.close()

            return df

    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

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

# Tab 2: Display TrollyOrder Table with Total Bill Calculation
with tab2:
    st.subheader("TrollyOrder Table")
    data_order = fetch_data("TrollyOrder")

    if not data_order.empty:
        st.dataframe(data_order)

        # Convert 'price' column to numeric and calculate total bill
        try:
            data_order["price"] = pd.to_numeric(data_order["price"], errors="coerce")  # Handle errors
            total_bill = data_order["price"].sum()
            st.success(f"**Total Bill: ₹{total_bill:.2f}**")  # Display total
        except Exception as e:
            st.error(f"Error calculating total bill: {e}")

    else:
        st.warning("No data found in TrollyOrder table.")
