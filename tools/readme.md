# 📌 Tools Package: `db_utils` & `log_config`

## **🔹 Overview**
This package provides essential utility functions for **database management (`db_utils`)** and **logging configuration (`log_config`)** to streamline application development.

### **📂 Package Structure**
```
tools_package/
│── db_utils.py        # Database management utilities
│── log_config.py      # Logging configuration utilities
│── __init__.py        # Package initializer
│── README.md          # Documentation
```

---

## **🛠 `db_utils.py` - Database Management**
`db_utils` provides a set of functions for managing **SQLite databases**, handling queries, inserts, updates, and schema setup.

### **🔹 Key Features**
✅ **Database Connection Management** – Open and close connections efficiently.  
✅ **Table Management** – Create, delete, and fetch tables dynamically.  
✅ **Data Querying & Manipulation** – Insert, update, and retrieve data easily.  
✅ **Schema Management** – Automate schema creation and ensure integrity.  

### **📌 Example Usage**
```python
from db_utils import Database

db = Database("my_database.db")

db.create_table("tasks", "id INTEGER PRIMARY KEY, task TEXT, completed INTEGER")
db.insert("tasks", "task, completed", ("Finish report", 0))

all_tasks = db.fetch_all("tasks")
print(all_tasks)

db.close()
```

### **🔹 Functions in `db_utils.py`**
| Function | Description |
|----------|------------|
| `create_table(table_name, schema)` | Creates a new table with the given schema. |
| `insert(table_name, columns, values)` | Inserts data into a table. |
| `fetch_all(table_name)` | Retrieves all records from a table. |
| `update(table_name, set_clause, condition, values)` | Updates records based on a condition. |
| `delete(table_name, condition, values)` | Deletes records matching a condition. |
| `remove_all_tables()` | Drops all tables from the database. |
| `fetch_column(table_name, column_name)` | Retrieves all unique values from a specified column. |

---

## **📌 `log_config.py` - Logging Utility**
`log_config` provides a **centralized logging setup**, ensuring consistent logging across all modules.

### **🔹 Key Features**
✅ **Modular Logging** – Reusable logging configuration for different modules.  
✅ **File & Console Logging** – Logs messages to a file and prints them to the console.  
✅ **Customizable Levels** – Supports `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  
✅ **Log Rotation** – Ensures logs do not grow indefinitely.

### **📌 Example Usage**
```python
from log_config import get_logger

logger = get_logger("task_manager", "task_manager.log")
logger.info("Task Manager initialized successfully")
```

### **🔹 Functions in `log_config.py`**
| Function | Description |
|----------|------------|
| `get_logger(logger_name, log_file)` | Initializes a logger with the specified name and file. |
| `close_log_handlers(logger)` | Closes all handlers for a logger (useful for cleanup). |

---

## **🚀 Installation & Usage**
1️⃣ Clone the repository:
```sh
git clone https://github.com/yourusername/tools_package.git
cd tools_package
```

2️⃣ Install dependencies (if needed):
```sh
pip install -r requirements.txt
```

3️⃣ Import utilities in your Python scripts:
```python
from db_utils import Database
from log_config import get_logger
```

---

## **🛠 Future Improvements**
- 🔹 Support for **PostgreSQL & MySQL** in `db_utils`
- 🔹 **Automatic database migrations**
- 🔹 **Advanced logging filters & formatting options**

---

## **📄 License**
This project is licensed under the **MIT License**.

---

## **🤝 Contributing**
Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## **📞 Contact**
For questions or feedback, reach out to **[your email]** or open an issue on GitHub.

