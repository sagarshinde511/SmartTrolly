import mysql.connector
import pandas as pd
import streamlit as st

# MySQL database connection details
host = "82.180.143.66"
user = "u263681140_students"
password = "testStudents@123"
database = "u263681140_students"

# Function to fetch data from the TrollyProducts table
def fetch_data():
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

            # Query to fetch all data from TrollyProducts
            query = "SELECT * FROM TrollyProducts"
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
st.title("TrollyProducts Data Viewer")

# Fetch and display data
data = fetch_data()

if not data.empty:
    st.write("### Table Data")
    st.dataframe(data)
else:
    st.warning("No data found or connection error.")

