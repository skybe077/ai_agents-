# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 10:26:09 2025

@author: user
"""
import random
import datetime

# Initialize task parameters
task_vol = 150  # Number of tasks to generate
day_range = [5, 180]  # Min and max days for due date

# Function to Generate Random Date Ranges
def random_date(start_date, day_range):
    """Generate a random start date and due date within the given range."""
    due_date = start_date + datetime.timedelta(days=random.randint(day_range[0], day_range[1]))
    return start_date.strftime("%Y-%m-%d"), due_date.strftime("%Y-%m-%d")

def gen_task_list(task_vol, day_range):
    categories = ["Finance", "Meetings", "Personal", "CEO Communication", "Project Management"]
    priorities = ["Low", "Medium", "High"]
    task_templates = {
        "Finance": ["File taxes", "Review budget", "Pay invoices", "Check investments", "Analyze expenses"],
        "Meetings": ["Weekly sync", "Client call", "Team meeting", "Project review", "One-on-one"],
        "Personal": ["Read AI research", "Go to the gym", "Buy groceries", "Plan vacation", "Visit family"],
        "CEO Communication": ["Prepare CEO report", "Email summary to CEO", "Review CEO notes", "Draft strategy", "Meet CEO"],
        "Project Management": ["Update sprint plan", "Review backlog", "Assign tasks", "Check milestones", "Plan retrospective"]
    }

    # Generate Task List
    curr_date = datetime.date.today()
    tasks = []
    for i in range(task_vol):
        category = random.choice(categories)
        task_name = task_templates[category][random.randint(0, 4)] 
        filed_date, due_date = random_date(curr_date, day_range)
        due_time = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"  # Random time
        priority = random.choice(priorities)
        completed = random.choice([0, 1])  # 0 for Pending, 1 for Completed
        days_until_due = (datetime.datetime.strptime(due_date, "%Y-%m-%d").date() - curr_date).days
        suggested_completion_date = (datetime.datetime.strptime(due_date, "%Y-%m-%d") - datetime.timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
    
        # Set actual completion date only if completed
        actual_completion_date = None
        if completed == 1:
            actual_completion_date = (datetime.datetime.strptime(due_date, "%Y-%m-%d") - datetime.timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")
    
        tasks.append([category, task_name, filed_date, due_date, due_time, priority, completed, days_until_due, suggested_completion_date, actual_completion_date])

    return tasks


# Table Schemas
table_schemas = {
    "category_table": """
        category TEXT PRIMARY KEY, 
        base_priority TEXT, 
        min_priority TEXT
    """,

    "task_list": """
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        category TEXT, 
        task TEXT, 
        filed_date TEXT,
        due_date TEXT, 
        due_time TEXT, 
        priority TEXT, 
        completed TEXT, 
        days_until_due INTEGER, 
        suggested_completion_date TEXT, 
        actual_completion_date TEXT
    """,

    "category_stats_table": """
        category TEXT PRIMARY KEY, 
        total_tasks INTEGER, 
        completed_tasks INTEGER, 
        overdue_tasks INTEGER, 
        first_task_date TEXT, 
        last_task_date TEXT, 
        avg_task_freq INTEGER, 
        completion_rate REAL
    """
}

categories = [
    ("Finance", "High", "Medium"),
    ("Meetings", "Medium", "Low"),
    ("Personal", "Low", "Low"),
    ("CEO Communication", "High", "High"),
    ("Project Management", "Medium", "Medium"),
]

category_stats = [
    ("Finance", 5, 3, 2, "2025-01-01", "2025-03-01", 60, 0.6),
    ("Meetings", 10, 9, 1, "2025-02-01", "2025-02-28", 7, 0.9),
    ("Personal", 8, 7, 1, "2025-01-15", "2025-02-25", 30, 0.88),
    ("CEO Communication", 3, 1, 2, "2025-01-10", "2025-02-20", 45, 0.33),
    ("Project Management", 6, 4, 2, "2025-01-05", "2025-02-27", 15, 0.67),
]

tasks = gen_task_list (task_vol, day_range)