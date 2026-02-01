#Refelction Questions:

# 1. What was the most challeniging part of the assignment for me?

# I would say the most difficult part of this assignment was troubleshooting the connection to the pstgresql server. Because while the code, environment variables, and dependencies were set up correctly,
# the connection consistnetly failed due to password authentication and possible server control issues. Debugging this required seperating issues between client side and server side.

#2. How did I overcome these challenges?

# I overcame these challenges by methodically testing each layer of the connection process. I verified that the variables were loading correctly, confirmed that the required libraries were installed,
#and used the psql client to directly test connectivity to the database. After I was able to more or less confirm that the issues were server side, I created a mock data set with the same structure as
#the real database output. This then allowed me to continue developing and testing the Pandas analysis logic.

# 3. What new concepts and skills did I learn from this assignment?

# Through this assignmnet I gained a much better understanding of how python interacts with databases using SQLAlchemy and how authentication and access control can possibly impact automated processes.
# I also learned to design scripts that can fail gracefully so to speak by detecting possible detection issues and switching to fallback data sources. And additionally I also strengtned my skills with
#pandas for grouping, aggregation, and time based data analysis.





#%% Import necessary libraries

# SQL Alchemy for database connection
from sqlalchemy import create_engine

# Pandas for Data Manipulation
import pandas as pd

# Dotenv and os for loading environment variables
from dotenv import load_dotenv
import os
import socket

# load environment variables from .env file no fail
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

#%% Set up database connection
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_port = os.getenv("db_port")
db_db = os.getenv("db_db")
db_host = os.getenv("db_host")

# Create PostgreSQL connection string
connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_db}"

#%%
# Query data from the database
query = "SELECT * FROM electricity.usage_data;"

def load_mock_df():
    # Mock dataset with the same columns I'll use in analysis
    return pd.DataFrame({
        "interval_end_date": pd.date_range("2025-01-01", periods=24 * 14, freq="h"),
        "kwh": [
            0.4 if (h % 24) < 6 else
            0.7 if (h % 24) < 12 else
            1.0 if (h % 24) < 18 else
            1.4
            for h in range(24 * 14)
        ]
    })

def load_df():
    # 1) Quick DNS check: if the host can’t be resolved, DB will never work on this machine
    try:
        socket.gethostbyname(db_host)
    except Exception as e:
        print("Cannot resolve DB host, using mock data")
        print("Reason:", repr(e))
        return load_mock_df()

    # 2) Try real DB read
    try:
        engine = create_engine(connection_string)
        df_real = pd.read_sql(query, engine)
        print(" Connected to Postgres and loaded real data")
        return df_real
    except Exception as e:
        print(" Could not connect/query Postgres. Using mock data")
        print("Reason:", repr(e))
        return load_mock_df()


df = load_df()

print("Data preview:")
print(df.head())



#%% Data Manipulation with Pandas

'''

Assignment Starts HERE

Your Assignment is to complete the following tasks using Pandas.  

You will then group all of these numbers into a single Dictionary with the following layout:

summary_dict = {
    "total_overall_usage": <value>,
    "monthly_usage": {
        "YYYY-MM": <value>,
        ...
    },
    "highest_month": {
        "month": "YYYY-MM",
        "usage": <value>
    },
    "highest_hourly_average": {
        "hour": <value>,
        "average_usage": <value>
    }
}
'''

# Task One: Display first few rows of the DataFrame

# Task Two: Calculate total overall usage (sum kwh)

# Task Three: Create a new column labeled "month" off of "interval_end_date"

# Task Three: Group by month and sum overall_usage (sum kwh by month and year)

# Task Four: Find the month with the highest overall usage

# Task Five: Find the Hour of the day with the highest average overall usage

# Finally: Fill out and print the summary dictionary

# Task One: Display first few rows of the DataFrame
print(df.head())

# Make sure columns are correct types
df["interval_end_date"] = pd.to_datetime(df["interval_end_date"], errors="coerce")
df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce")
df = df.dropna(subset=["interval_end_date", "kwh"])

# Task Two: Calculate total overall usage (sum kwh)
total_overall_usage = float(df["kwh"].sum())

# Task Three: Create a new column labeled "month" off of "interval_end_date"
df["month"] = df["interval_end_date"].dt.to_period("M").astype(str)

# Task Three: Group by month and sum kwh by month and year
monthly_usage_series = df.groupby("month")["kwh"].sum().sort_index()
monthly_usage = {k: float(v) for k, v in monthly_usage_series.to_dict().items()}

# Task Four: Find the month with the highest overall usage
highest_month = str(monthly_usage_series.idxmax())
highest_month_usage = float(monthly_usage_series.max())

# Task Five: Find the hour of the day with the highest average overall usage
df["hour"] = df["interval_end_date"].dt.hour
hourly_avg_series = df.groupby("hour")["kwh"].mean()
highest_hour = int(hourly_avg_series.idxmax())
highest_hour_avg = float(hourly_avg_series.max())

summary_dict = {
    "total_overall_usage": total_overall_usage,
    "monthly_usage": monthly_usage,
    "highest_month": {
        "month": highest_month,
        "usage": highest_month_usage
    },
    "highest_hourly_average": {
        "hour": highest_hour,
        "average_usage": highest_hour_avg
    }
}
print(summary_dict)

monthly_usage_series.plot(title="Overall Usage Trend (kWh by Month)")



# Assignment Bonus (Optional - 10 points):
# Using Pandas, create a line plot that shows the trend of overall usage over time (by month).

# Assignment Easter Egg (Optional - 5 points):
# Why would we not be able to compare these values year over year?

# Year over year comparison can be misleading if you don't have complete years of data,
# or if major factors changed (weather, occupancy, appliances)

'''

    Assignment Ends Here

'''
