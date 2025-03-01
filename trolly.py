import mysql.connector
from mysql.connector import Error

try:
    # Establish the database connection
    connection = mysql.connector.connect(
        host="82.180.143.66",
        user="u263681140_students",
        password="testStudents@123",
        database="u263681140_students"
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Query to fetch all data from TrollyProducts table
        query = "SELECT * FROM TrollyProducts"
        cursor.execute(query)

        # Fetch all rows
        records = cursor.fetchall()

        # Display the records
        for row in records:
            print(row)

        # Close cursor and connection
        cursor.close()
        connection.close()

except Error as e:
    print("Error while connecting to MySQL:", e)
