# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 14:50:53 2025

A SQLite3 Utility package to abstract database ops 
Currently used in AI Agent learning

The way to use this utility package is 
1. Create a Database object (db) which connects to an SQLIte DB 
2. Pass db variable around your main script to add, remove, create tables etc


@author: user
"""
import sqlite3
from log_config import get_logger, close_log_handlers
import os

# Initialize logger
db_logger = get_logger("db_utils", "db_utils.log")

class Database:
    def __init__(self, db_name="data.db"):
        """Initialize the database connection."""
        
        self.db_name = db_name
        self.db_logger = db_logger
        
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.db_logger.info(f"Connected to database: {db_name}")
        except Exception as e:
            self.db_logger.error(f"Failed to connect to database: {e}")
    
    def database_exists(self):

        """Check if the database file exists before connecting."""
        return os.path.exists(self.db_name)

    def remove_all_tables(self):
        """Drop all tables from the database."""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            if ('sqlite_sequence',) in tables:             
                tables.remove(('sqlite_sequence',))
            
            for table in tables:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
            self.conn.commit()
            self.db_logger.info("All tables removed successfully.")
        except Exception as e:
            self.db_logger.error(f"Error removing all tables: {e}")

        
    def create_table(self, table_name, schema):
        """Create a table with the given name and schema."""
        try:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            self.conn.commit()
            self.db_logger.info(f"Table '{table_name}' created with schema: {schema}")
        except Exception as e:
            self.db_logger.error(f"Error creating table '{table_name}': {e}")

    def insert(self, table_name, columns, values):
        """Insert a new record into the specified table."""
        try:
            placeholders = ", ".join(["?" for _ in values])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.db_logger.info(f"Inserted into '{table_name}': {values}")
        except Exception as e:
            self.db_logger.error(f"Error inserting into '{table_name}': {e}")

    def insert_many(self, table_name, columns, values_list):
        """Insert multiple records into the specified table."""
        try:
            placeholders = ", ".join(["?" for _ in values_list[0]])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.executemany(query, values_list)
            self.conn.commit()
            self.db_logger.info(f"Inserted {len(values_list)} records into '{table_name}'")
        except Exception as e:
            self.db_logger.error(f"Error inserting multiple records into '{table_name}': {e}")

    def fetch_all(self, table_name):
        """Fetch all records from the specified table."""
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            self.db_logger.info(f"Fetched {len(rows)} records from '{table_name}'")
            return rows
        
        except Exception as e:
            self.db_logger.error(f"Error fetching from '{table_name}': {e}")
            return []

    def fetch_column_names(self, table_name):
        """Fetches column names for a given table."""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in self.cursor.fetchall()]
            self.db_logger.info(f"Fetched columns for table '{table_name}': {columns}")
            return columns
        except Exception as e:
            self.db_logger.error(f"Error fetching columns for '{table_name}': {e}")
            return []

    def update(self, table_name, set_clause, condition, values):
        """Update records in the specified table."""
        try:
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.db_logger.info(f"Updated '{table_name}' with {set_clause} where {condition}")
        except Exception as e:
            self.db_logger.error(f"Error updating '{table_name}': {e}")

    def delete(self, table_name, condition, values):
        """Delete records from the specified table."""
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.db_logger.info(f"Deleted from '{table_name}' where {condition}")
        except Exception as e:
            self.db_logger.error(f"Error deleting from '{table_name}': {e}")

    def close(self):
        """Close the database connection."""
        try:
            self.conn.close()
            self.db_logger.info("Database connection closed.")
        except Exception as e:
            self.db_logger.error(f"Error closing the database connection: {e}")   
            
    def has_data(self):
        """Check if any table in the database has data."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
    
        if ('sqlite_sequence',) in tables:             
            tables.remove(('sqlite_sequence',))
    
        for table in tables:
            table_name = table[0]
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            if count > 0:
                return True  # Found data
    
        return False  # No data in any table

    def stop_db(self):
        self.db_logger.info("Closing DB connection and log handlers.")
        close_log_handlers(self.db_logger)
        self.close()

    def fetch_column(self, table_name, column_name):
        """
        Fetches all distinct values from a specific column in a table.
    
        Parameters:
            table_name (str): The name of the database table.
            column_name (str): The column to retrieve.
    
        Returns:
            list: A list of values from the specified column.
        """
        try:
            query = f"SELECT DISTINCT {column_name} FROM {table_name}"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Extract only the first value of each row
            return [row[0] for row in results]
    
        except Exception as e:
            self.db_logger.error(f"Error fetching column '{column_name}' from '{table_name}': {e}")
            return []