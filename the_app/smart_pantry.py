# spell-checker: disable
"""
smart_pantry.py
A Streamlit app to manage pantry items:
- Add products with expiry dates
- Track days left until expiration
- Save data in a CSV file
Date: 22/10/2025
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
        pd.DataFrame: DataFrame with columns ['Product', 'Expiry Date', 'Category']
                    or empty DataFrame if file not found.
    """
    try:
        # Try to read existing xlsx file
        df = pd.read_excel("the_app/data/pantry_data.xlsx")
        # Convert 'Expiry Date' column to datetime type
        df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
        return df
    except FileNotFoundError:
        # If no file found, return empty DataFrame with correct column names
        return pd.DataFrame(
            columns=["Product", "Category", "Expiry Date", "Quantity", "Days Left"]
        )


# Load data when the app starts
data = load_data()

# ---------- Add New Product ----------
st.write("### ➕ Add a new product")
# Input fields for product name and expiry date
product = st.text_input("Product name:")
category = st.selectbox(
    "Category:",
    [
        "Uncategorized",
        "Bakery",
        "Fruits",
        "Vegetables",
        "Meat",
        "Seafood",
        "Dairy",
        "Protein",
        "Condiments",
        "Grains",
        "Snacks",
        "Beverages",
        "Frozen Foods",
        "Canned Goods",
        "Spices & Seasonings",
        "Drinks",
    ],
)
expiry = st.date_input("Expiry date:")

quantity = st.number_input("Quantity:", min_value=1, value=1)

# When user clicks 'Save product' button
if st.button("Save product"):
    if product:
        # Get today's date
        today = datetime.now().date()
        # Calculate days left until expiry
        days_left = (expiry - today).days
        # Create a new row with the entered data
        new_row = {
            "Product": product,
            "Category": category,
            "Expiry Date": expiry,
            "Quantity": quantity,
            "Days Left": days_left,
        }
        # Add the new row to the existing data
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        # Save updated data to excel file (persistent storage)
        data.to_excel("the_app/data/pantry_data.xlsx", index=False)
        st.cache_data.clear()  # Clear cache so the table refreshes
        # Display success message
        st.success(f"✅ {product} added and saved successfully!")
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

    # ---------- Display Data ----------

st.write("### 🧾 Pantry Items List")

if not data.empty:
    data = data.sort_values("Expiry Date")

    # ---------- Alert System ----------
    today = pd.Timestamp(datetime.now().date())
    data["Days Left"] = (data["Expiry Date"] - today).dt.days

    expired = data[data["Days Left"] < 0]
    expiring_soon = data[(data["Days Left"] >= 0) & (data["Days Left"] <= 3)]

    # Display alerts first
    if not expired.empty:
        st.error("⚠️ Some products have expired:")
        st.table(expired[["Product", "Expiry Date", "Days Left"]])

    if not expiring_soon.empty:
        st.warning("⏰ Some products are expiring soon:")
        st.table(expiring_soon[["Product", "Expiry Date", "Days Left"]])

    # Then show the full list of products

    def color_days(val):
        """Return a background color based on days left."""
        if val < 0:
            color = "#ff0000"  # red (expired)
        elif val <= 3:
            color = "#ffee00"  # yellow (expiring soon)
        else:
            color = "#00fb00"  # green (safe)
        return f"background-color: {color}; color: black;"

    styled_data = data.reset_index(drop=True).style.applymap(
        color_days, subset=["Days Left"]
    )
    st.write("### 🧾 Pantry Items List")
    st.dataframe(styled_data)
    # st.dataframe(data.reset_index(drop=True))
else:
    st.info("No products added yet. Use the form above to add one.")
