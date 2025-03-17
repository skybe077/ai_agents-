# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 12:51:16 2025

Task utilities to insert, update tasks 


@author: user
"""

import datetime

from db_utils.task_mgr_db import TaskManagerDB 
from ai_utils import parse_task_ai, categorise_task_ai
import ml_utils 
from log_config import get_logger
import config

'''
CONFIGURE Logger
'''
logger = get_logger(config.task_logger_name, config.task_logger_file)  

def insert_task(user_input, model, table_name = "task_list"):
        
        
    logger.info(f"INSERT TASK: Starting Insert Task for this input: {user_input}")
    task_priority = "Medium" # defaut task priority

    """ 
    Parsing the Task using OPENAI
    Gets Task, due date, due time 
    """ 
    
    task_name, due_date, due_time = parse_task_ai(user_input)
    
    logger.info(f"INSERT TASK: || Parsing complete. Task: {task_name} & due_date: {due_date} * due time: {due_time}")
    
    if not task_name or not due_date:
        logger.error(f"INSERT TASK: || Failed to parse input: {user_input}")
        return False
    
    """ 
    Categorising the Task using OPENAI
    """ 

    logger.info(f"INSERT TASK: || Categorising Task: {task_name}")
    category = categorise_task(task_name)
    logger.info(f"INSERT TASK: || Finished Categorising & interest Task: {task_name} \n Category: {category}")


    """ 
    Gets duration until due
    """ 

    today = datetime.date.today()
    days_until_due = (due_date - today).days


    """ 
    Insert task into DB 
    """
    try:    
        db = TaskManagerDB(config.db_name)
        col_names = db.fetch_column_names(table_name)
        col_names.remove("id")
        
        # ✅ Get AI-suggested completion date
        # workload_today = get_task_count_for_today()  # Function to count today's tasks
        completed_tasks = len(db.get_task(completed=1))
        logger.info(f"TO INSERT TASK: || Task '{task_name}' added under category '{category}' ")

        logger.info(f"TO INSERT TASK: Category Encoder Classes: '{ml_utils.category_encoder.classes_}'")
        logger.info(f"TO INSERT TASK: Priority Encoder Classes: '{ml_utils.priority_encoder.classes_}'")

        if completed_tasks < 50 :
            suggested_completion_date = suggest_task_date(due_date, task_priority, days_until_due, category)
        else: 
            suggested_completion_date = suggest_task_date_ml(due_date, task_priority, days_until_due, category, model)
            
        logger.info(f"TO INSERT TASK: || Task '{task_name}' added under category '{category}' with due date {due_date}, days_until_due: {days_until_due}, suggested_completion_date: {suggested_completion_date}")
        
        db.insert(table_name, 
                  ",".join(col_names),
            (category, task_name, today.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d"), due_time.strftime("%H:%M:%S"), task_priority, 0, days_until_due, suggested_completion_date, None)
        )
    
        
        db.close() 
        logger.info(f"INSERT TASK: || Task '{task_name}' added under category '{category}' with due date {due_date}.")

    except Exception as e:
        logger.error(f"INSERT TASK: || Error inserting into '{table_name}': {e}")
        
    """ 
    Update Category Stats 
    """
        
    update_category_stats(category)
    
    logger.info(f"UPDATED CATEGORY: || Task '{task_name}' added under category '{category}' with due date {due_date}.")

    return True


def suggest_task_date(due_date, priority, days_until_due, category):
    """
    Hybrid ML Task Scheduling: 
    - Uses Weighted Scoring if user has < 50 completed tasks.
    - Uses ML if user has enough historical data.
    """
    # ✅ Use weighted scoring for new users
    priority_weight = {"Low": 5, "Medium": 3, "High": 1}
    workload_penalty = 2 #if workload_today > 3 else 0
    suggested_days = max(1, days_until_due - priority_weight[priority] - workload_penalty)
    
    return (datetime.date.today() + datetime.timedelta(days=suggested_days)).strftime("%Y-%m-%d")
    

def suggest_task_date_ml(due_date, priority, days_until_due, category, model):
    # ✅ Use ML model for experienced users
    
    formatted_task = ml_utils.format_task_for_prediction(due_date, priority, category, days_until_due)
    logger.info(f"SUGGEST DATE ML: || Formatted Task '{formatted_task}.")

    predicted_days = ml_utils.predict_task_date_with_ml(formatted_task, model)    
    logger.info(f"SUGGEST DATE ML: || Predicted Days: '{int(predicted_days[0])}.")

    predicted_days = days_until_due if int(predicted_days[0]) > days_until_due else int(predicted_days[0])

    return (datetime.date.today() + datetime.timedelta(days=predicted_days)).strftime("%Y-%m-%d")
    # return predict_task_date_with_ml(user_id, due_date, priority, workload_today)    



def categorise_task(task_description):
    
    """
    # Step 1: GET OpenAI to suggest a category based on task description
    """
    
    ai_suggested_category = categorise_task_ai(task_description)

    """
    # Step 2: Check if Category Exists in current DB 
    """
    
    db = TaskManagerDB(config.db_name)
    
    existing_categories = [row[0] for row in db.fetch_all("category_table")]

    if ai_suggested_category in existing_categories:
        logger.info(f"CATEGORISE TASK: Step 2: AI found a match in category db: {ai_suggested_category}\n returning to calling function")
        return ai_suggested_category  # Exact match found

    """
    # Step 3: Try Finding a Close Match
    """
    import difflib

    logger.info("CATEGORISE TASK: Step 3: Looking for closest match in category db")
    
    closest_match = difflib.get_close_matches(ai_suggested_category, existing_categories, n=1, cutoff=0.7)
    
    if closest_match:        
        logger.info(f"CATEGORISE TASK: Step 3: Found closest match in category db: \n a. Closest match in DB:  {closest_match[0]} \n b. AI Suggested Category: ai_suggested_category")
        return closest_match[0]  # Use the closest matching existing category

    """
    # Step 4: No Match Found, Create a New Category. Set Min Priority to Medium
    """
    logger.info("CATEGORISE TASK: Step 4: No match. Make a new entry")

    new_category = ai_suggested_category
    db.insert("category_table", "category, base_priority, min_priority", (new_category, "Medium", "Medium"))
    db.close()
    
    logger.info("CATEGORISE TASK: Step 4: New entry made in category table")
    
    return new_category  



def update_category_stats(category):
    """
    Recalculates and updates category statistics & dynamically adjusts category priority
    while ensuring it does not drop below the minimum priority level.
    """
    logger.info(f"Updating category stats for: {category}")
    
    db = TaskManagerDB(config.db_name)

    try:
        """
        # Fetch category's min_priority
        """
        cat_info = db.get_category_info (category)
        min_priority = cat_info["min_priority"] if cat_info["min_priority"] else "Low"  # Default to Low if not set

        logger.info(f"UPDATE stats for: {category} // Getting data from DB")
        
        # Get updated stats from task_list
        result = db.task_stats_by_(category)

        logger.info(f"UPDATE stats for: {category} // Got Result: {result}")

        if result:
            total_tasks = result["total_tasks"]
            completed_tasks = result["completed_tasks"]
            overdue_tasks = result["overdue_tasks"]
            first_task_date = result["first_task_date"]
            last_task_date = result["last_task_date"]

            """
            # CALCULATE rates 
            """
            completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0
            avg_task_freq = (
                (datetime.datetime.strptime(last_task_date, "%Y-%m-%d") - datetime.datetime.strptime(first_task_date, "%Y-%m-%d")).days // total_tasks
                if total_tasks > 1 else 0
            )

            logger.info(f"UPDATE stats for: {category} // Calculated Completion Rate: {completion_rate} & Avg Task Rate: {avg_task_freq}")

            """
            # **Dynamic Priority Adjustments**
            """
            
            if overdue_tasks > 3:
                new_priority = "High"
            elif total_tasks > 10 and completion_rate > 0.8:
                new_priority = "Low"
            elif total_tasks > 10 and overdue_tasks < 2:
                new_priority = "Medium"
            else:
                new_priority = "Medium"  # Default priority

            """
            # **Ensure new_priority does not drop below min_priority**
            """
            
            priority_levels = ["Low", "Medium", "High"]
            new_priority_index = priority_levels.index(new_priority)
            min_priority_index = priority_levels.index(min_priority)

            if new_priority_index < min_priority_index:
                new_priority = min_priority  # Prevent downgrade below min_priority

            """
            # Update category_stats_table & category_table
            """

            db.upsert_category_stats(category, total_tasks, completed_tasks, overdue_tasks, first_task_date, last_task_date, avg_task_freq, completion_rate)
            db.update("category_table", "base_priority = ?", "category = ?", (new_priority, category))
                    
            logger.info(f"Updated category stats & priority for {category} to {new_priority}")

    except Exception as e:
        logger.error(f"Error updating category stats: {e}")

    finally:
        db.close()


def update_task_completion(task_id, updated_status):
    """Marks a task as completed and updates category stats."""
    logger.info(f"Completing task: {task_id}")

    curr_date = datetime.date.today()

    db = TaskManagerDB(config.db_name)

    try:
        """
        GET task information 
        """ 
        task_info = db.get_task(id=task_id)
        col_names = db.fetch_column_names("task_list")
 
        if not task_info:
            logger.error(f"Task ID '{task_id}' not found in database.")
            db.close()
            return False
    
        logger.info(f"Updating Task '{task_id}' to {updated_status}.")
        
        # Update the task status to 'Completed'
        db.update("task_list", "completed = ?, actual_completion_date =?", "id = ?", (updated_status, curr_date.strftime("%Y-%m-%d"), task_id,))        
        
        logger.info(f"Task '{task_id}' updated to {updated_status}.")

        logger.info(f"Task '{task_id}' updating category stats.")
        # **Update category statistics after task completion**
        category = task_info[0][col_names.index("category")] # Get Category 
        update_category_stats(category)

        logger.info(f"Task '{task_id}' updated category stats.")

        db.close()
        return True

    except Exception as e:
        logger.error(f"Error marking task as completed: {e}")
        db.close()
        return False
    
    
def learn_sched_pattern():
    """
        For completed task cout > 50. Train a decision tree.
        Use complete_in_days as Target
        Return predictor
    """

    # 1. Pull completed tasks from task list

    logger.info("LEARN Scheduling Patterns:")

    db = TaskManagerDB(config.db_name)

    try:
        """
        GET task information 
        """ 
        completed_tasks = db.get_task(completed=1)
        col_names = db.fetch_column_names("task_list")

        db.close()

        if len(completed_tasks) < 50: 
            logger.error("LEARN: Fewer than 50 completed tasks. No need for an ML approach")            
            return None

    except Exception as e:
        logger.error(f"LEARN: Error with pulling data from DB: {e}")
        return None
    
    try:    
        logger.info("LEARN: Formatting for learning")
        
        ml_utils.init_encoders()
        df = ml_utils.format_for_learning(completed_tasks, col_names)
        
        logger.info(f"LEARN: Category Encoder Classes: '{ml_utils.category_encoder.classes_}'")
        logger.info(f"LEARN: Priority Encoder Classes: '{ml_utils.priority_encoder.classes_}'")
        
        logger.info(f"LEARN: Task count '{len(completed_tasks)}'. Starting with Decision Trees")
        best_model, best_params, best_score = ml_utils.learn_decision_tree(df, "complete_in_days")
        
        logger.info(f"LEARN: best_model '{best_model}'. best_params: '{best_params}'. best_score: '{best_score}'")
        
        return [best_model, best_params, best_score]
        
    except Exception as e:
        logger.error(f"LEARN: Error with creating a predictor prediction: {e}")
        db.close()
        return None
    
    finally:
        db.close()
        
        