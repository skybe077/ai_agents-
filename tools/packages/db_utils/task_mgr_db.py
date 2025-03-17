# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 09:47:55 2025

@author: user
"""

from db_utils import Database
import sqlite3


class TaskManagerDB(Database):
    
    def __init__(self, db_name="data.db"):
        """Initialize the database connection."""
                
        super().__init__(db_name)
        self.db_logger.info("TaskManagerDB: initialized successfully") 




    def get_task(self, **filters):
        """
        Retrieve tasks based on dynamic filters.
        
        Usage:
            get_task(id=1)                     # Get task by ID
            get_task(category="Meetings")       # Get tasks in "Meetings"
            get_task(priority="High")           # Get all High priority tasks
            get_task(completed="Pending")       # Get all pending tasks
            get_task(category="Finance", priority="High")  # Multiple filters
        """
            
        try:
            if not filters:
                query = "SELECT * FROM task_list"
                values = ()
            else:
                conditions = " AND ".join([f"{key} = ?" for key in filters.keys()])
                query = f"SELECT * FROM task_list WHERE {conditions}"
                values = tuple(filters.values())
    
            self.cursor.execute(query, values)
            results = self.cursor.fetchall()
    
            self.conn.commit()
            self.db_logger.info(f"Fetched tasks with filters: {filters}")
            
            return results 
    
        except Exception as e:
            self.db_logger.error(f"Error fetching tasks with filters {filters}: {e}")
            return None
        
        
    def upsert_category_stats(self, category, total_tasks, completed_tasks, overdue_tasks, first_task_date, last_task_date, avg_task_freq, completion_rate):
        """Inserts or updates category stats in `category_stats_table`."""
        try:
            query = """
            INSERT INTO category_stats_table (category, total_tasks, completed_tasks, overdue_tasks, first_task_date, last_task_date, avg_task_freq, completion_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(category) 
            DO UPDATE SET 
                total_tasks = excluded.total_tasks,
                completed_tasks = excluded.completed_tasks,
                overdue_tasks = excluded.overdue_tasks,
                first_task_date = excluded.first_task_date,
                last_task_date = excluded.last_task_date,
                avg_task_freq = excluded.avg_task_freq,
                completion_rate = excluded.completion_rate;
            """
            self.cursor.execute(query, (category, total_tasks, completed_tasks, overdue_tasks, first_task_date, last_task_date, avg_task_freq, completion_rate))
            self.conn.commit()
            self.db_logger.info(f"Upsert successful for category '{category}'")
        except Exception as e:
            self.db_logger.error(f"Error in upsert operation for '{category}': {e}")

    def get_category_info (self, category):
        """
        GETS category stats 
        """
        try:
            
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            query = """
             SELECT * 
             FROM category_table
             WHERE category = ?
             """
            self.cursor.execute(query, (category,))
            row = self.cursor.fetchone()  # Fetch row as a tuple        
            self.conn.commit()
            
            return self.convert_row_to_dict(row)
            
        except Exception as e:
            self.db_logger.error(f"Error getting CATEGORY INFO  for '{category}': {e}")
            return None       


    def task_stats_by_(self, category):
        """
        GETS category stats from task List
        """
        try:
            
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            query = """
             SELECT 
                 COUNT(*) AS total_tasks, 
                 SUM(CASE WHEN completed = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks, 
                 SUM(CASE WHEN days_until_due < 0 THEN 1 ELSE 0 END) AS overdue_tasks, 
                 MIN(due_date) AS first_task_date, 
                 MAX(due_date) AS last_task_date 
             FROM task_list 
             WHERE category = ?
             """
            self.cursor.execute(query, (category,))
            row = self.cursor.fetchone()  # Fetch row as a tuple        
            self.conn.commit()

            if row:
                # Convert row object to dictionary
                stats = dict(row)
                self.db_logger.info(f"GOT CATEGORY STATS for '{category}': {stats}")
                return stats  # Returns a dictionary instead of a tuple
            else:
                self.db_logger.warning(f"No data found for category '{category}'")
                return None
            
        except Exception as e:
            self.db_logger.error(f"Error getting CATEGORY STATS for '{category}': {e}")
            return None       

    '''
        UTility functions
    '''



    def convert_row_to_dict(self, row):
        if row:
            # Convert row object to dictionary
            stats = dict(row)
            self.db_logger.info(f"Converted Row to dictionary: {stats}")
            return stats  # Returns a dictionary instead of a tuple
        else:
            self.db_logger.warning(f"No data found")
            return None

                
    ''' 
        Create tables and populate data specifically for Task Manager Agent
        Tables created: 
        . category_table
        . task_list
        . category_stats_table
    '''

    def create_all_task_mgr_tables(self, table_schemas):
        """Creates all necessary tables for the Task Manager system."""

        for table, schema in table_schemas.items():
            self.create_table(table, schema)
        self.db_logger.info("TaskManagerDB: All tables successfully created.")


    def get_column_names(self, table_name, table_schemas):
        """
        Extracts column names from TABLE_SCHEMAS in config.py.
        """
        if table_name in table_schemas:
            schema = table_schemas[table_name]
            columns = [col.split()[0] for col in schema.split(",")]  # Extract only column names
            return columns
        else:
            return None  # Table name not found

    def populate_task_mgr_data(self, data_config):
        """
        Populates initial task list, category stats, and category table.
        """
        try:
            # Insert Categories from config
            self.insert_many("category_table", "category, base_priority, min_priority", data_config.categories)
            # Insert Tasks from config
            self.insert_many("task_list","category, task, filed_date, due_date, due_time, priority, completed, days_until_due, suggested_completion_date, actual_completion_date", data_config.tasks)
            # Insert Category Stats from config
            self.insert_many("category_stats_table", "category, total_tasks, completed_tasks, overdue_tasks, first_task_date, last_task_date, avg_task_freq, completion_rate", data_config.category_stats)
            self.db_logger.info("TaskManagerDB: Data successfully populated from config.")

        except Exception as e:
            self.db_logger.error(f"TaskManagerDB: Error populating task data: {e}") 
