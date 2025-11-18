import os
import sqlite3

import pandas as pd

# Path to the original CSV file
csv_path = "the_app/data/Recipe_Dataset.csv"

# SQLite database file (same base name as the CSV)
sqlite_path = "the_app/data/Recipe_Dataset.sqlite"

# Check if the CSV file exists before loading
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

# Load the CSV data into a pandas DataFrame
df = pd.read_csv(csv_path)

# Create the SQLite database and write the DataFrame into a table named "recipes"
conn = sqlite3.connect(sqlite_path)
df.to_sql("recipes", conn, if_exists="replace", index=False)

# Close the database connection
conn.close()
