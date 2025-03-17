# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 13:37:30 2025

@author: user
"""

import datetime
import pandas as pd
from sklearn import preprocessing 
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
        
        
# Store label encoders for categories and priorities
category_encoder = None
priority_encoder = None


def init_encoders():
    global category_encoder 
    global priority_encoder
    
    category_encoder = preprocessing.LabelEncoder()
    priority_encoder = preprocessing.LabelEncoder()
    
    import numpy as np
    priority_map = ["Low", "Medium", "High"]

    # Set classes explicitly (Must match the order in `priority_mapping`)
    priority_encoder.fit(priority_map)
    priority_encoder.classes_ = np.array(priority_map)
    
    
def encode_category(df, column_name):
    """Encodes a categorical column dynamically using LabelEncoder."""
    if column_name in df.columns:
        df[column_name] = category_encoder.fit_transform(df[column_name])
    return df

def encode_priority(df, column_name):
    """Encodes priority column dynamically."""
    # Define a fixed mapping
    if column_name in df.columns:
        df[column_name] = priority_encoder.transform(df[column_name])
    return df
    
    return df


def format_for_learning(completed_tasks, col_names):
    
    df = pd.DataFrame(completed_tasks)
    df.columns = col_names

    # convert dates to datetime 
    df['filed_date'] = pd.to_datetime(df['filed_date'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['actual_completion_date'] = pd.to_datetime(df['actual_completion_date'])
    
    
    # find the difference between actual_completion_date and filed_Date
    df['complete_in_days'] = (df['actual_completion_date'] - df['filed_date']).dt.days
    
    # label encode Priority and category
    df = encode_priority(df, "priority")
    df = encode_category(df, "category")

    # drop id, task, filed_date, due_date, completed, suggested_completion_date, actual_completion_date         
    df.drop(columns=["id", "task", "filed_date", "due_date", "due_time", "completed", "suggested_completion_date", "actual_completion_date"], axis=1, inplace=True)
    
    return df

def learn_decision_tree(df, target):
    
    # Spilt into train and test sets 
    variables = list(df.columns)
    variables.remove(target)
    
    X_train, X_test, y_train, y_test = train_test_split(df[variables], df[target], test_size = 0.2, shuffle=True)

    # Define Decision Tree Model
    model = DecisionTreeRegressor(random_state=42)

    # Define GridSearchCV parameters
    param_grid = {
        "max_depth": [3, 5, 10, None],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4]
    }

    # Run GridSearchCV
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring="r2", n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    # Get Best Model, Parameters, and Score
    best_model = grid_search.best_estimator_
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_

    return best_model, best_params, best_score


def format_task_for_prediction(due_date, priority, category, days_until_due):
    """
    Converts a task into the expected dataset format for prediction.
    Handles new categories dynamically.

    Parameters:
        task (str): Task description (Not used in prediction)
        due_date (str): Due date in "YYYY-MM-DD" format
        priority (str): Task priority ("Low", "Medium", "High")
        category (str): Task category
    
    Returns:
        pd.DataFrame: Formatted input for model prediction
    """
    
    # Convert priority to numeric using the trained encoder
    if priority in priority_encoder.classes_:
        priority_numeric = priority_encoder.transform([priority])[0]
    else:
        priority_numeric = 2  # Default to "Medium" if unseen

    # Convert category to numeric using the trained encoder
    if category in category_encoder.classes_:
        category_numeric = category_encoder.transform([category])[0]
    else:
        category_numeric = max(category_encoder.classes_.shape[0], 1)  # Assign next available ID
        
    # Format as a DataFrame
    formatted_task = pd.DataFrame([{
        "category": category_numeric,
        "priority": priority_numeric,
        "days_until_due": days_until_due
    }])

    return formatted_task


def predict_task_date_with_ml(formatted_task, model):
    predicted_days = model.predict(formatted_task)

    return predicted_days

