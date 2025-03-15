import sqlite3
from exception import CustomException
from logger import logger
import sys
DB_PATH = "D:\Projects\GenAI\Senor 2.0\Backend\data source\IndiaLaw.db" 

def fetch_data():
    conn = None  

    try:
        logger.info("Trying to access DB")
        conn = sqlite3.connect(DB_PATH) 
        cursor = conn.cursor()

        # Get column names
        cursor.execute("PRAGMA table_info(cpc);")
        columns = [col[1] for col in cursor.fetchall()] 
        
        query = "SELECT * FROM cpc LIMIT 1;"
        cursor.execute(query)

        cursor.execute(query)
        rows = cursor.fetchall()

        logger.info("DB read successful")
        
        print("\nColumn Names:", columns)
        print("Data from cpc table:")
        for row in rows:
            formatted_row = {columns[i]: row[i] for i in range(len(columns))}
            print(formatted_row)

    except sqlite3.Error as e:
        logger.error(f"Error accessing database: {str(e)}")
        raise CustomException(e, sys)

    finally:
        if conn: 
            conn.close()

fetch_data()