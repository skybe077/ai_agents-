# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 11:19:09 2025
!streamlit run taskManager.py

@author: user
"""
from log_config import get_logger, close_log_handlers
from db_utils.task_mgr_db import TaskManagerDB 
import task_utils
import streamlit as st
import config
import data_config


class TaskManager():
    
    def __init__(self, db_name="data.db"):
        """Initialize Task Manager instance"""
                
        self.db_name = config.db_name
        self.gpt_model = config.gpt_model 
        self.logger = get_logger(config.task_logger_name, config.task_logger_file)
        self.completed_tasks = 0
        self.best_model = None
        self.best_params = None
        self.best_score = None
        self.init(False)
        
        self.logger.info("TaskManager: initialized successfully") 
        
        
    """"
    TASK MANAGER UTITLITY FUNCTIONS 
    """
    def init(self, reset = 0):
        
        self.logger.info(f"Task Manager INIT. Reset is {reset}. ")
        
        db = TaskManagerDB(self.db_name)
        
        if 'app_stop' not in st.session_state:
            st.session_state['app_stop'] = False

        if reset:
            self.logger.info("Task Manager INIT: Getting Reset. Removing all tables")
            db.remove_all_tables()
            
        if not db.has_data():
            self.logger.info(f"Task Manager INIT: Reset is {reset}. Creating all tables")
            db.create_all_task_mgr_tables(data_config.table_schemas)
            db.populate_task_mgr_data(data_config)
    
            self.logger.info(f"Task Manager INIT: Reset is {reset}. Task Manager DB created & populated.")
        else: 
            self.logger.error(f"Task Manager INIT: Reset is {reset}. Skip creating with dummy data.")
        
        completed_tasks = len(db.get_task(completed=1))   
        
        db.close()
        self.logger.info(f"Task Manager INIT: Reset is {reset}. Completed task in DB:'{completed_tasks}'. Completed Task in TaskManager:'{self.completed_tasks}'")
        
        if completed_tasks > (self.completed_tasks + 10): 
            self.logger.info(f"Task Manager INIT: Reset is {reset}. Training a decision tree.")
                
            model = task_utils.learn_sched_pattern()
            self.best_model = model[0]
            self.best_params = model[1]
            self.best_score = model[2]
            self.completed_tasks = completed_tasks

        self.logger.info(f"Task Manager INIT: Reset is {reset}. Completed task in DB:'{completed_tasks}'. Completed Task in TaskManager:'{self.completed_tasks}'")


    
    def stop_app(self):
        
        """Stop Streamlit app and close log handlers."""
        
        self.logger.info("Stopping Streamlit app and closing log handlers.")
        close_log_handlers(self.logger)
        st.warning("App has been stopped. Restart required to continue.")
        
        db = TaskManagerDB(self.db_name)
        db.stop_db()
    
        st.stop() 

    
    """"
    DISPLAY FUNCTIONS 
    """
    
    ### Create Input Section
    def display_input(self):
        ####
        # DISPLAY input 
        ####                  
        st.header("Add a New Task")
        task_input = st.text_input("Enter your task in natural language (e.g., 'Prepare slides for Friday at 10 AM')")
            
        # Create columns for button layout
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
        
        with col1:
            if st.button("Add Task"):
                task_inserted = task_utils.insert_task(task_input, self.best_model)
                 
                if task_inserted:            
                    st.success("Task added successfully!")
                else:
                    st.error("Failed to parse your input. Please try again.")
                    self.logger.warning("At Main: Failed to parse user input.")
    

        if not st.session_state['app_stop']:
            with col2: 
                if st.button("Stop App"):
                    st.session_state['app_stop'] = True
                    st.rerun()

        if st.session_state['app_stop']:
           with col2: 
               if st.button("Start App"):
                   st.session_state['app_stop'] = False
                   st.rerun()
                               
           with col3: 
               if st.button("Reset App"):
                   st.session_state['app_stop'] = True
                   self.init(True)
                   st.success("Task Manager is reset")
                           
           self.stop_app()  # Stop Streamlit & close logs



 
                
    ### List Tasks Section
    def display_tasks(self, table_name = "task_list", check_col = "completed"):
        import pandas as pd 
                
        ###
        #Get tasks from DB        
        ###
        
        db = TaskManagerDB(self.db_name)
        
        tasks = db.fetch_all(table_name)
        col_names = db.fetch_column_names(table_name)
        disabled_cols = list(filter(lambda x: x != check_col, col_names))
        
        db.close()
        ## close DB        
        
        self.logger.info("Got tasks & column names from DB")
        
        ####
        #CREATE Task list 
        ####
        st.header("Your Task List")
        
        if tasks:
            df = pd.DataFrame(tasks, columns=col_names)
                
            # Create Editable Table for Completion Toggle
            edited_df = st.data_editor(df, column_config={check_col: st.column_config.CheckboxColumn(check_col)}, disabled = disabled_cols)
        

            ####
            # CHECK each row to see if there 
            ####
            
            for index, row in edited_df.iterrows():
                original_status = df.loc[index, check_col]
                updated_status = row[check_col]

                #st.write(f"✅ Task {row['task']} at row id {row['id']} has original_status = {original_status}")
                
                if original_status != updated_status:  # Only update if status changes
                    success = task_utils.update_task_completion(row["id"], updated_status)
                    
                    if success:
                        #st.write(f"✅ Task '{row['task']}' has been updated! Task original_status = {original_status} now it's updated_status = {updated_status}")
                        st.rerun()  # Refresh table after updates      
                        st.success(f"Updated task '{row['task']}'!")
                  
                    else:
                        st.error(f"❌ Failed to update task '{row['task']}'.")
        
        else:
            st.warning("No tasks found!")

    def sidebar(self):

        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
            

        st.sidebar.page_link("TaskManager.py", label="View All Tasks")
        st.sidebar.page_link("pages/category_stats.py", label="View Category Stats")     

  
# Entry point
if __name__ == "__main__":
    
    if "task_manager" not in st.session_state:
            st.session_state.task_manager = TaskManager()

    task_manager = st.session_state.task_manager     

    st.set_page_config(page_title="Task Manager", layout="wide")
    task_manager.sidebar() 
    
    task_manager.display_input()
    task_manager.display_tasks()      


