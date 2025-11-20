"""
smart_pantry.py
Smart Pantry Web App (Home Page Only)

Features:
- Each user has a personal pantry (saved to Excel)
- Add, edit, and track products with expiry alerts
- Quantity + Unit input (supports numeric + count)
- Small loading animation when saving
- Optional intro demo video

Date: 29/10/2025
"""

import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

# Constants
DATA_DIR = "smart_pantry_manager/data"
EXPIRY_SOON_DAYS = 3

# ---------- Page Setup ----------
st.set_page_config(page_title="Smart Pantry Manager", page_icon="🧺", layout="centered")

st.title("📱 Smart Pantry Manager 📊")
st.subheader("Track your pantry items and discover what you can cook 👇")

# ---------- Sidebar: User Profile ----------
st.sidebar.header("👤 User Profile")
username = st.sidebar.text_input("Enter your name or email:")

if not username:
    st.warning("Please enter your name to start using the app.")
    st.stop()

st.session_state["username"] = username
os.makedirs(DATA_DIR, exist_ok=True)

user_file = os.path.join(DATA_DIR, f"pantry_{username.replace(' ', '_').lower()}.xlsx")


# ---------- Load Pantry ----------
@st.cache_data
def load_pantry(file_path: str) -> pd.DataFrame:
    """Load pantry data for a user or create an empty table."""
    try:
        df = pd.read_excel(file_path)
        df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
        df["Days Left"] = (df["Expiry Date"] - datetime.now()).dt.days
        # Remove expired items automatically
        df = df[df["Days Left"] >= 0].reset_index(drop=True)
        return df
    except FileNotFoundError:
        columns = [
            "Product",
            "Category",
            "Quantity",
            "Unit",
            "Expiry Date",
            "Days Left",
        ]
        return pd.DataFrame(columns=columns)


pantry_data = load_pantry(user_file)

# ---------- Add New Product ----------
st.header("➕ Add a New Product")
product_name = st.text_input("Product name:")
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
quantity = st.number_input("Quantity (numeric or count):", min_value=0.0, step=0.1)
unit = st.selectbox("Unit:", ["count", "g", "kg", "ml", "L", "cup", "tbsp", "tsp"])
expiry_date = st.date_input("Expiry date:")

if st.button("💾 Save product"):
    if product_name:
        with st.spinner("💾 Saving product... please wait..."):
            time.sleep(1)
            today = datetime.now().date()
            days_left = (expiry_date - today).days
            new_row = {
                "Product": product_name,
                "Category": category,
                "Quantity": quantity,
                "Unit": unit,
                "Expiry Date": expiry_date,
                "Days Left": days_left,
            }
            pantry_data = pd.concat(
                [pantry_data, pd.DataFrame([new_row])], ignore_index=True
            )
            pantry_data.to_excel(user_file, index=False)
            st.cache_data.clear()
        st.success(f"✅ {product_name} added successfully!")
    else:
        st.warning("Please enter a product name.")

# ---------- Update Days Left ----------
if not pantry_data.empty:
    pantry_data["Expiry Date"] = pd.to_datetime(
        pantry_data["Expiry Date"], errors="coerce"
    )
    today = pd.Timestamp(datetime.now().date())
    pantry_data["Days Left"] = (pantry_data["Expiry Date"] - today).dt.days

# ---------- Alerts ----------
st.header("⚠️ Expiry Alerts")
if not pantry_data.empty:
    expired = pantry_data[pantry_data["Days Left"] <= 0]
    expiring_soon = pantry_data[
        (pantry_data["Days Left"] > 0) & (pantry_data["Days Left"] <= EXPIRY_SOON_DAYS)
    ]

    if not expired.empty:
        st.error("❌ Some products have expired:")
        st.table(expired[["Product", "Expiry Date", "Days Left"]])

    if not expiring_soon.empty:
        st.warning("⏰ Some products are expiring soon:")
        st.table(expiring_soon[["Product", "Expiry Date", "Days Left"]])

# ---------- Pantry Table ----------
st.header("📦 Your Pantry Items")


def color_days(val: int) -> str:
    """Return background color based on days left."""
    if val < 0:
        color = "#ff4d4d"
    elif val <= EXPIRY_SOON_DAYS:
        color = "#ffcc00"
    else:
        color = "#85e085"
    return f"background-color: {color}; color: black;"


if not pantry_data.empty:
    # Sort by Days Left (ascending) so soon-to-expire items are first
    display_data = pantry_data.sort_values(by="Days Left", ascending=True)
    styled_data = display_data.reset_index(drop=True).style.applymap(
        color_days, subset=["Days Left"]
    )
    st.dataframe(styled_data, use_container_width=True)
else:
    st.info("Your pantry is empty. Add your first product above!")


# ---------- Manual Save ----------
if st.button("🔄 Save Changes"):
    if "data" in globals() and not data.empty:
        # Sort by Days Left ascending before saving
        sorted_data = data.sort_values(by="Days Left", ascending=True)
        # Ensure USER_FILE is defined
        user_file = f"smart_pantry_manager/data/pantry_{username.replace(' ', '_').lower()}.xlsx"
        sorted_data.to_excel(user_file, index=False)
        st.success("Pantry data saved successfully (sorted by expiry)!")
    else:
        st.info("No items to save.")
