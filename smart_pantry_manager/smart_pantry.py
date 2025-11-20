# spell-checker: disable
"""
smart_pantry.py
Smart Pantry Web App (Home Page Only)

Features:
- Personal pantry for each user (saved to Excel)
- Add, edit, and track products with expiry alerts
- Quantity + unit input (numeric or count)
- Small loading animation when saving
- Optional intro/demo video

Date: 29/10/2025
"""

import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

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

# Create user-specific file path
os.makedirs("smart_pantry_manager/data", exist_ok=True)
USER_FILE = os.path.join(
    "smart_pantry_manager", "data", f"pantry_{username.replace(' ', '_').lower()}.xlsx"
)


# ---------- Load Pantry ----------
@st.cache_data
def load_pantry(file_path):
    """Load pantry data or create empty DataFrame."""
    try:
        df = pd.read_excel(file_path)
        df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
        df["Days Left"] = (df["Expiry Date"] - datetime.now()).dt.days
        df = df[df["Days Left"] >= 0].reset_index(drop=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame(
            columns=[
                "Product",
                "Category",
                "Quantity",
                "Unit",
                "Expiry Date",
                "Days Left",
            ]
        )


data = load_pantry(USER_FILE)

# ---------- Add New Product ----------
st.header("➕ Add a New Product")
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
quantity = st.number_input("Quantity (numeric or count):", min_value=0.0, step=0.1)
unit = st.selectbox("Unit:", ["count", "g", "kg", "ml", "L", "cup", "tbsp", "tsp"])
expiry = st.date_input("Expiry date:")

if st.button("💾 Save product"):
    if product:
        with st.spinner("💾 Saving product... please wait..."):
            time.sleep(1)
            today = datetime.now().date()
            days_left = (expiry - today).days
            new_row = {
                "Product": product,
                "Category": category,
                "Quantity": quantity,
                "Unit": unit,
                "Expiry Date": expiry,
                "Days Left": days_left,
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            data.to_excel(USER_FILE, index=False)
            st.cache_data.clear()
        st.success(f"✅ {product} added successfully!")
    else:
        st.warning("Please enter a product name.")

# ---------- Update Days Left ----------
if not data.empty:
    data["Expiry Date"] = pd.to_datetime(data["Expiry Date"], errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    data["Days Left"] = (data["Expiry Date"] - today).dt.days

# ---------- Alerts ----------
st.header("⚠️ Expiry Alerts")
if not data.empty:
    expired = data[data["Days Left"] < 0]
    expiring_soon = data[(data["Days Left"] >= 0) & (data["Days Left"] <= 3)]
    if not expired.empty:
        st.error("❌ Some products have expired:")
        st.table(expired[["Product", "Expiry Date", "Days Left"]])
    if not expiring_soon.empty:
        st.warning("⏰ Some products are expiring soon:")
        st.table(expiring_soon[["Product", "Expiry Date", "Days Left"]])

# ---------- Pantry Table ----------
st.header("📦 Your Pantry Items")


def color_days(val):
    if val < 0:
        color = "#ff4d4d"
    elif val <= 3:
        color = "#ffcc00"
    else:
        color = "#85e085"
    return f"background-color: {color}; color: black;"


if not data.empty:
    # Sort by Days Left ascending
    data_sorted = data.sort_values("Days Left").reset_index(drop=True)
    styled_data = data_sorted.style.applymap(color_days, subset=["Days Left"])
    st.dataframe(styled_data, use_container_width=True)
else:
    st.info("Your pantry is empty. Add your first product above!")

# ---------- Manual Save ----------
if st.button("🔄 Save Changes"):
    data.to_excel(USER_FILE, index=False)
    st.success("Pantry data saved successfully!")
