import sqlite3
import sys
from exception import CustomException
from logger import logger

class DatabaseManager:
    """Class to manage database operations"""
    
    def __init__(self, db_path):
        """Initialize with database path"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        try:
            logger.info(f"Connecting to database at {self.db_path}")
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise CustomException(e, sys)
    
    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {query} - {str(e)}")
            raise CustomException(e, sys)
    
    def get_table_columns(self, table_name):
        """Get columns for a specific table"""
        try:
            self.connect()
            query = f"PRAGMA table_info({table_name});"
            results = self.execute_query(query)
            columns = [col[1] for col in results]
            logger.info(f"Retrieved columns for table '{table_name}'")
            return columns
        finally:
            self.disconnect()
    
    def get_all_tables(self):
        """Get all tables in the database"""
        try:
            self.connect()
            query = "SELECT name FROM sqlite_master WHERE type='table';"
            results = self.execute_query(query)
            tables = [table[0] for table in results]
            logger.info(f"Retrieved {len(tables)} tables from database")
            return tables
        finally:
            self.disconnect()
    
    def fetch_table_data(self, table_name, limit=10):
        """Fetch data from a specific table with optional limit"""
        try:
            self.connect()
            columns = self.get_table_columns(table_name)
            
            # Reconnect since the previous method disconnected
            self.connect()
            query = f"SELECT * FROM {table_name} LIMIT {limit};"
            rows = self.execute_query(query)
            
            formatted_data = []
            for row in rows:
                formatted_row = {columns[i]: row[i] for i in range(len(columns))}
                formatted_data.append(formatted_row)
            
            logger.info(f"Retrieved {len(formatted_data)} rows from table '{table_name}'")
            return formatted_data
        finally:
            self.disconnect()

# def main():
#     DB_PATH = "data source/IndiaLaw.db" 
#     db_manager = DatabaseManager(DB_PATH)
    
    
#     # Print all tables in the database
#     print("Available tables in the database:")
#     tables = db_manager.get_all_tables()
#     for i, table in enumerate(tables, 1):
#         print(f"{i}. {table}")
    
#     # Get columns for a specific table
#     table_name = 'cpc'
#     print(f"\nColumns in '{table_name}' table:")
#     columns = db_manager.get_table_columns(table_name)
#     for i, column in enumerate(columns, 1):
#         print(f"{i}. {column}")
    
#     # Get data from a specific table
#     print(f"\nData from '{table_name}' table:")
#     data = db_manager.fetch_table_data(table_name, limit=1)
#     for i, row in enumerate(data, 1):
#         # print(f"Row {i}:")
#         for column, value in row.items():
#             print(f"{column}: {value}")
#         print()

# if __name__ == "__main__":
#     try:
#         main()
#     except CustomException as e:
#         print(f"An error occurred: {e}")

"""
Available tables in the database:
1. IPC
2. NIA
3. IEA
4. CRPC
5. HMA
6. CPC
7. IDA
8. MVA
"""

DB_PATH = "data source/IndiaLaw.db" 
db_manager = DatabaseManager(DB_PATH)