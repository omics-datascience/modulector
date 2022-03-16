import os
import psycopg2
from psycopg2 import Error
try:
    USER = os.getenv('POSTGRES_USERNAME')
    PASSWORD = os.getenv('POSTGRES_PASSWORD')
    PORT = os.getenv('POSTGRES_PORT')
    DB = os.getenv('POSTGRES_DB')
    HOST = os.getenv('POSTGRES_HOST')
 
    # Connect to an existing database
    connection = psycopg2.connect(user=USER,
                                  password=PASSWORD,
                                  host=HOST,
                                  port=PORT,
                                  database=DB)

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Executing a SQL query
    cursor.execute("select * from modulector_mirna limit 1;")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - modulector-db")
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

except:
    print("Error while connecting to PostgreSQL\n")
    exit(1)
