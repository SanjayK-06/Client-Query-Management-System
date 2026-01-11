# db_connect.py

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """
    Create and return a PostgreSQL connection using .env values.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Database connected successfully!")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

if __name__ == "__main__":
    # Test the database connection
    connection = get_connection()
    if connection:
        connection.close()