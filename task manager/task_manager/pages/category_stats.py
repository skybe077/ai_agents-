# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 15:26:04 2025

@author: user
"""

import streamlit as st
import pandas as pd
import db_utils
import config


db_name = config.db_name


def display_category():
    
    db = db_utils.Database(db_name)
    
    st.title("📊 Category & Task Statistics")
    
    # --- 📂 Category Table ---
    st.header("📂 Task Categories")
    
    category_data = db.fetch_all("category_table")
    
    if category_data:
        category_df = pd.DataFrame(category_data, columns=["Category", "Base Priority", "Min Priority"])
        st.dataframe(category_df, width=800, height=300)
    else:
        st.warning("No categories found!")    

    db.close()
    
def display_cat_stats():

    db = db_utils.Database(db_name)
    
    # --- 📈 Category Statistics Table ---
    st.header("📈 Category Statistics")
    
    category_stats_data = db.fetch_all("category_stats_table")
    
    if category_stats_data:
        category_stats_df = pd.DataFrame(
            category_stats_data,
            columns=[
                "Category", "Total Tasks", "Completed Tasks", "Overdue Tasks",
                "First Task Date", "Last Task Date", "Avg Task Frequency", "Completion Rate"
            ]
        )
        
        # Convert Dates
        category_stats_df["First Task Date"] = pd.to_datetime(category_stats_df["First Task Date"]).dt.strftime("%Y-%m-%d")
        category_stats_df["Last Task Date"] = pd.to_datetime(category_stats_df["Last Task Date"]).dt.strftime("%Y-%m-%d")
        
        # Sort by Most Active Categories
        category_stats_df = category_stats_df.sort_values(by="Total Tasks", ascending=False)
        
        st.dataframe(category_stats_df, width=1200, height=400)
    else:
        st.warning("No category statistics found!")
    
    db.close()    
    
    
def main():

    display_category()
    display_cat_stats()    


# Entry point
if __name__ == "__main__":

    main()
    
    
    


