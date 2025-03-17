# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 13:06:09 2025

AI utility script 
Parse 
Categorise 

@author: user
"""

from openai import OpenAI
from dateutil import parser
import datetime

from log_config import get_logger
import config

#OPENAI_API_KEY = "" # input your OPENAI key here for testing only. This script puts Open AI secret key in its environment variables
 
'''
CONFIGURE Logger
'''
logger = get_logger(config.task_logger_name, config.task_logger_file)  

def parse_task_ai(user_input):
    
    """
    Get Current Date 
    """
    curr_date = datetime.date.today().strftime("%A, %B %d, %Y")  # Full date for context (e.g., Friday, February 14, 2025)
    logger.info(f"PARSE TASK: Received user input for task parsing: '{user_input}'")
    
    client = OpenAI()
    #client = OpenAI(api_key=OPENAI_API_KEY) # creates an OpenAI object with your AP KEY for testing only. Comment out the line above 

    """
    SET UP Message to OpenAI 
    """

    try:
        response = client.chat.completions.create(
            model= config.gpt_model,
            messages=[
                {"role": "system", "content": f"You are a task parser. Today is {curr_date}. Your job is to accurately extract the task and calculate the correct due date relative to today. The due date should reflect the closest matching day and time."},
                {"role": "user", "content": f"Input: '{user_input}'. Return the output in the format 'task: [task], due_date: [due_date]'."}
            ],
            max_tokens=100,
            temperature=0.2
        )

        """
        Receive response from Open AI
        """
        
        output = response.choices[0].message.content
        logger.info(f"PARSE TASK: OpenAI response: {output}")

        task = output.split("task: ")[1].split(", due_date:")[0].strip()
        due_date = output.split("due_date: ")[1].strip()
        due_date_parsed = parser.parse(due_date)

        logger.info(f"PARSE TASK: Parsed task: {task}, Parsed due date: {due_date_parsed}")
        return task, due_date_parsed.date(), due_date_parsed.time()

    except Exception as e:
        logger.error(f"PARSE TASK: Error parsing task: {e}")
        return None, None, None


def categorise_task_ai(task_description):
    """
    Use AI to categorize a task and map it to an existing category.
    """
    
    logger.info(f"CATEGORISE TASK: Categorising task now: {task_description}")

    client = OpenAI()
    #client = OpenAI(api_key=OPENAI_API_KEY) # creates an OpenAI object with your AP KEY for testing only. Comment out the line above     
    """
    # Step 1: AI Suggests a Category
    """
    
    response = client.chat.completions.create(
        model= config.gpt_model,
        messages=[
            {"role": "system", "content": "You are an AI that assigns tasks to categories. "
                                          "Respond only with a category name."},
            {"role": "user", "content": f"Task: {task_description}"}
        ]
    )
    
    ai_suggested_category = response.choices[0].message.content.strip()

    logger.info(f"CATEGORISE TASK: Step 1: AI Categorised task as: {ai_suggested_category}")

    return ai_suggested_category 

