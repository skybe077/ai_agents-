# 📌 AI Task Manager Documentation

## **1️⃣ Executive Summary**
The **AI Task Manager** is an intelligent system that automates task scheduling, prioritization, and completion tracking. It integrates AI and machine learning to analyze user behavior and dynamically adjust priorities, making task management more efficient.

### **Why AI-powered Task Scheduling?**
- Automates **task parsing & categorization**
- Predicts **task completion time** using ML
- **Adapts dynamically** to changing workloads

### **🔹 Key Features**
✅ **AI-Powered Task Categorization** – Uses OpenAI to classify tasks
✅ **Dynamic Priority Adjustment** – Based on due dates & workload
✅ **ML-Based Completion Prediction** – Decision Trees predict completion time
✅ **User-Friendly Web Interface** – Streamlit-based task manager
✅ **Secure & Scalable** – Uses SQLite with modular APIs

---

## **2️⃣ System Architecture**
### **📂 Project Structure**
```
AI_Task_Manager/
│── taskManager.py          # Main Streamlit app
│── ai_utils.py             # AI-related functions (task parsing, categorization)
│── task_utils.py           # Task management functions (insert, update, complete)
│── category_stats.py       # Category analytics and reporting
│── data_config.py          # Default Task Manager database schemas and data sets
│── config.py               # System configuration: GPT model, log handle names 
│── README.md               # Documentation

Tools/
│── db_utils/
│   ├── task_mgr_db.py      # Task Manager Database manager for the agent. Sub class of db_utils
│   ├── db_utils.py      	# Generic SQLiteD Database manager. 
│   ├── __init__.py         # Package initializer
│── log_config/
│   ├── log_config.py      	# Logger setup. Creates and closes logger handles.  
│   ├── __init__.py         # Package initializer

```

---

## **3️⃣ AI & Machine Learning**
### **📌 How AI is Used?**
- **Task Categorization:** Uses OpenAI to classify tasks into predefined categories.
- **Task Completion Prediction:** Uses a Decision Tree model to estimate time needed to complete a task.
- **Handling New Categories:** Dynamically assigns IDs to new categories without requiring retraining.

### **🔹 ML Pipeline**
1️⃣ **Preprocessing:** Converts dates, encodes priority & category
2️⃣ **Training:** Decision Tree trained on past tasks (`complete_in_days` as target)
3️⃣ **Prediction:** ML estimates expected completion time

---

## **4️⃣ Database Schema & API**
### **📊 Table Definitions**
```sql
CREATE TABLE category_table (
    category TEXT PRIMARY KEY,
    base_priority TEXT,
    min_priority TEXT
);

CREATE TABLE task_list (
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
);

CREATE TABLE category_stats_table (
    category TEXT PRIMARY KEY,
    total_tasks INTEGER,
    completed_tasks INTEGER,
    overdue_tasks INTEGER,
    first_task_date TEXT,
    last_task_date TEXT,
    avg_task_freq INTEGER,
    completion_rate REAL
);
```
### **🔹 API Operations**
- **Insert Task** → Adds new tasks into `task_list`
- **Update Task Completion** → Marks tasks as completed & updates stats
- **Fetch Category Stats** → Retrieves task progress by category

---

## **5️⃣ UI & User Experience**
- **Streamlit-Based Web App** for interactive task management
- **Task Completion Toggles** to mark tasks as done
- **Task Analytics Dashboard** showing category-wise stats

---

## **6️⃣ Deployment & Security**
### **🔒 Running the Task Manager**
Run the Task Manager locally:
```sh
streamlit run taskManager.py
```
### **🔒 Securing OpenAI API Key**
- Store API keys in `.streamlit/secrets.toml` instead of hardcoding.
- Use **environment variables**:
```python
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## **7️⃣ Future Improvements**
I have stopped development on this task manager as it is a proof of concept on how tos use LLMs within an agentic framework.
🔹 **Google Calendar Integration** – Sync task deadlines with calendar
🔹 **Automated Notifications** – Alerts for approaching due dates
🔹 **Multi-User Access** – Shared task management for teams

---

## **8️⃣ Conclusion**
The **AI Task Manager** integrates **AI, ML, and automation** to streamline **task management and scheduling**. It provides **intelligent predictions, priority adjustments, and a user-friendly interface** to boost productivity.
