"""
smart_pantry.py

A Streamlit app to manage pantry items:
- Add products with expiry dates
- Track days left until expiration
- Save data in a CSV file

Date: 19/10/2025
"""

from datetime import datetime  # For working with dates and calculating days left

import pandas as pd  # For handling tabular data (DataFrame, CSV)
import streamlit as st  # For building the web app interface

# ---------- Page Setup ----------
st.set_page_config(
    page_title="Smart Pantry Manager",  # Title displayed in browser tab
    page_icon="🧺",  # Icon for the app
    layout="centered",  # Centered page layout
)
st.title("📱 Smart Pantry Manager 📊")  # Main title of the app
st.subheader(
    "Track your pantry items before they expire 👇"
)  # Subtitle for user guidance


# ---------- Load or Create Data ----------
@st.cache_data
# caches the output of the function so it doesn't reload
# every time the app reruns, improving performance when reading data
def load_data():
    """
    Load existing pantry data from 'pantry_data.csv'.

    Returns:
        pd.DataFrame: DataFrame with columns ['Product', 'Expiry Date', 'Days Left']
                    or empty DataFrame if file not found.
    """
    try:
        # Try to read existing CSV file
        df = pd.read_csv("the_app/data/pantry_data.csv")
        # Convert 'Expiry Date' column to datetime type
        df["Expiry Date"] = pd.to_datetime(
            df["Expiry Date"], errors="coerce", infer_datetime_format=True
        )
        return df
    except FileNotFoundError:
        # If no file found, return empty DataFrame with correct column names
        return pd.DataFrame(columns=["Product", "Expiry Date", "Days Left"])


# Load data when the app starts
data = load_data()

# ---------- Add New Product ----------
st.write("### ➕ Add a new product")
# Input fields for product name and expiry date
product = st.text_input("Product name:")
expiry = st.date_input("Expiry date:")

# When user clicks 'Save product' button
if st.button("Save product"):
    if product:
        # Get today's date
        today = datetime.now().date()
        # Calculate days left until expiry
        days_left = (expiry - today).days
        # Create a new row with the entered data
        new_row = {"Product": product, "Expiry Date": expiry, "Days Left": days_left}
        # Add the new row to the existing data
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        # Save updated data to CSV file (persistent storage)
        data.to_csv("the_app/data/pantry_data.csv", index=False)
        # Display success message
        st.success(f"✅ {product} added successfully!")
    else:
        # Show warning if product name is empty
        st.warning("Please enter a product name.")

# ---------- Update Days Left ----------
if not data.empty:
    # Ensure the column is properly converted to datetime
    data["Expiry Date"] = pd.to_datetime(
        data["Expiry Date"], errors="coerce", infer_datetime_format=True
    )

    # Drop any rows where conversion failed (invalid date)
    data = data.dropna(subset=["Expiry Date"])

    # Calculate days left safely
    today = pd.Timestamp(datetime.now().date())
    data["Days Left"] = (data["Expiry Date"] - today).dt.days
