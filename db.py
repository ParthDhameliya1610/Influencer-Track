import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

class DatabaseHelper:
    def __enter__(self):
        self.conn = get_db_connection()
        if self.conn is None:
            raise Exception("Database connection failed.")
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor, self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    with DatabaseHelper() as (cursor, conn):
        cursor.execute(query, params or ())
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        return cursor.lastrowid

def execute_write(query, params=None):
    with DatabaseHelper() as (cursor, conn):
        cursor.execute(query, params or ())
        return cursor.lastrowid