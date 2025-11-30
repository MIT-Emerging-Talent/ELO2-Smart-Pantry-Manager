"""
smart_pantry.py
Smart Pantry Web App (Home Page Only)

Features:
- Personal pantry for each user, stored in Excel
- Add, edit, and track products with automatic expiry alerts
- Support for numeric quantities and units (e.g., g, kg, ml, count)
- Visual indicators for soon-to-expire and expired items
- Optional loading animation when saving
- Optional demo video to guide new users

Date: 27/11/2025
"""

import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st


# ----- Styling Functions -----
def style_expired(expired_products_df):
    return expired_products_df.style.set_properties(
        **{
            "background-color": "#EB4343",  # Light Red
            "color": "black",
        }
    )


def style_expiring_soon(expiring_products_df):
    return expiring_products_df.style.set_properties(
        **{
            "background-color": "#F5DB76",  # Light Yellow
            "color": "black",
        }
    )


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
os.makedirs("smart_pantry_manager/data/user_data", exist_ok=True)
USER_FILE = f"smart_pantry_manager/data/user_data/pantry_{username.replace(' ', '_').lower()}.xlsx"


# ---------- Load Pantry ----------
@st.cache_data
def load_pantry(file_path):
    """Load pantry data for a specific user or create empty table."""
    try:
        df = pd.read_excel(file_path)
        df["Expiry Date"] = pd.to_datetime(df["Expiry Date"], errors="coerce")
        df["Days Left"] = (df["Expiry Date"] - datetime.now()).dt.days

        # Remove expired items automatically
        # df = df[df["Days Left"] >= 0].reset_index(drop=True)
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


pantry_df = load_pantry(USER_FILE)

# Store in session_state
if "pantry_data" not in st.session_state:
    st.session_state["pantry_data"] = pantry_df

# ---------- Add New Product ----------
st.header("➕ Add a New Product")

product_name = st.text_input("Product name:")
product_category = st.selectbox(
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
        "Milks & Alternatives",
        "Drinks",
    ],
)
product_quantity = st.number_input(
    "Quantity (numeric or count):", min_value=0.0, step=0.1
)
product_unit = st.selectbox(
    "Unit:", ["count", "g", "kg", "ml", "L", "cup", "tbsp", "tsp"]
)
expiry_date = st.date_input("Expiry date:")

if st.button("💾 Save product"):
    if product_name:
        with st.spinner("💾 Saving product... please wait..."):
            time.sleep(2)
            today = datetime.now().date()
            days_left = (expiry_date - today).days
            new_product = {
                "Product": product_name,
                "Category": product_category,
                "Quantity": product_quantity,
                "Unit": product_unit,
                "Expiry Date": expiry_date,
                "Days Left": days_left,
            }
            pantry_df = st.session_state["pantry_data"]
            pantry_df = pd.concat(
                [pantry_df, pd.DataFrame([new_product])], ignore_index=True
            )

            # Sort by Days Left
            pantry_df = pantry_df.sort_values(
                by="Days Left", ascending=True
            ).reset_index(drop=True)
            pantry_df.to_excel(USER_FILE, index=False)
            st.session_state["pantry_data"] = pantry_df
            st.cache_data.clear()
        st.success(f"✅ {product_name} added successfully!")
    else:
        st.warning("Please enter a product name.")

# ---------- Update Days Left ----------
if not st.session_state["pantry_data"].empty:
    pantry_df = st.session_state["pantry_data"]
    pantry_df["Expiry Date"] = pd.to_datetime(pantry_df["Expiry Date"], errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    pantry_df["Days Left"] = (pantry_df["Expiry Date"] - today).dt.days
    st.session_state["pantry_data"] = pantry_df

# ---------- Alerts ----------
st.markdown("### ⚠️ Expiry Alerts")

current_df = st.session_state["pantry_data"]  # renamed

if not current_df.empty:
    expired_items = current_df[current_df["Days Left"] <= 0].copy()  # renamed
    expired_items = expired_items.sort_values(by="Days Left")
    expiring_items = current_df[
        (current_df["Days Left"] > 0) & (current_df["Days Left"] <= 5)
    ].copy()  # renamed

    # ---------- Expired Products ----------
    if not expired_items.empty:
        with st.expander("❌ Expired Products (Click to view)", expanded=True):
            st.dataframe(
                style_expired(expired_items[["Product", "Expiry Date", "Days Left"]]),
                use_container_width=True,
            )
            col1, col2 = st.columns([2, 1])
            if col2.button("🗑️ Delete ALL expired"):
                current_df = current_df[current_df["Days Left"] >= 0]
                st.session_state["pantry_data"] = current_df
                current_df.to_excel(USER_FILE, index=False)

                st.success("All expired products deleted!")

    # ---------- Expiring Soon ----------
    if not expiring_items.empty:
        with st.expander("⏰ Expiring Soon (Within 3 days)", expanded=True):
            st.dataframe(
                style_expiring_soon(
                    expiring_items[["Product", "Expiry Date", "Days Left"]]
                ),
                use_container_width=True,
            )

    # ---------- Manage Section ----------
    st.markdown("---")
    st.markdown("### 🛠 Manage Products")

    colA, colB = st.columns([2, 3])
    selected_item = colA.selectbox("Choose a product:", current_df["Product"].unique())

    if selected_item:
        item_row = current_df[current_df["Product"] == selected_item].iloc[0]
        colB.markdown(f"**Current:** {item_row['Quantity']} {item_row['Unit']}")

        new_quantity = colB.number_input(
            "New quantity:",
            min_value=0.0,
            max_value=float(item_row["Quantity"]),
            value=float(item_row["Quantity"]),
            step=0.1,
        )

        col1, col2 = st.columns([1, 1])
        if col1.button("✔️ Update Quantity"):
            current_df.loc[current_df["Product"] == selected_item, "Quantity"] = (
                new_quantity
            )
            st.session_state["pantry_data"] = current_df
            current_df.to_excel(USER_FILE, index=False)
            st.success("Quantity updated!")

        if col2.button("🗑️ Delete Product"):
            current_df = current_df[current_df["Product"] != selected_item]
            st.session_state["pantry_data"] = current_df
            current_df.to_excel(USER_FILE, index=False)
            st.success(f"{selected_item} deleted!")

st.markdown("---")

# ---------- Pantry Table ----------
st.header("📦 Your Pantry Items")


def color_days(val):
    """Color based on days left."""
    if val < 0:
        color = "#ff4d4d"
    elif val <= 3:
        color = "#ffcc00"
    else:
        color = "#85e085"
    return f"background-color: {color}; color: black;"


if not pantry_df.empty:
    display_data = pantry_df.sort_values(by="Days Left", ascending=True)
    styled_data = display_data.reset_index(drop=True).style.applymap(
        color_days, subset=["Days Left"]
    )
    st.dataframe(styled_data, use_container_width=True)
else:
    st.info("Your pantry is empty. Add your first product above!")

# ---------- Manual Save ----------
if st.button("🔄 Save Changes"):
    if not pantry_df.empty:
        pantry_df_sorted = pantry_df.sort_values(by="Days Left", ascending=True)
        pantry_df_sorted.to_excel(USER_FILE, index=False)
        st.session_state["pantry_data"] = pantry_df_sorted
        st.success("Pantry data saved successfully (sorted by expiry)!")
    else:
        st.info("No items to save.")
