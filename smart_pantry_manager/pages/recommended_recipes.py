# spell-checker: disable
"""
Recipe Recommendation Page for Smart Pantry Application
"""

import os
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Recommended Recipes", page_icon="🍳", layout="wide")

st.title("🍳 Recommended Recipes")
st.caption("Discover recipes you can cook with what’s already in your pantry!")

# ---------- Check username ----------
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please go to the Home page and enter your username first.")
    st.stop()

username = st.session_state["username"]
USER_FILE = f"the_app/data/pantry_{username.replace(' ', '_').lower()}.xlsx"

# ---------- Load pantry ----------
try:
    pantry = pd.read_excel(USER_FILE)
    pantry["Product"] = pantry["Product"].astype(str).str.lower()
except FileNotFoundError:
    st.info("Your pantry is empty. Please add items on the Home page.")
    st.stop()

# ---------- Auto remove expired items ----------
if "Expiry Date" in pantry.columns:
    before = len(pantry)
    pantry = pantry[
        pd.to_datetime(pantry["Expiry Date"], errors="coerce") >= pd.Timestamp.today()
    ]
    if len(pantry) < before:
        st.warning(
            f"⏰ Removed {before - len(pantry)} expired item(s) from your pantry automatically."
        )


# ---------- Load recipes ----------
@st.cache_data
def load_recipes():
    """Load recipes from the SQLite database and clean up column names."""
    db_path = os.path.join("the_app", "data", "Recipe_Dataset.sqlite")

    if not os.path.exists(db_path):
        st.error(
            "⚠️ Recipes database not found. Please create Recipe_Dataset.sqlite inside the_app/data/."
        )
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)

    # Read the 'recipes' table
    df = pd.read_sql_query("SELECT * FROM recipes", conn)

    conn.close()

    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {
        "title": "Recipe",
        "cleaned_ingredients": "Ingredients",
        "instruction": "Instructions",
        "instructions": "Instructions",
    }

    df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True
    )

    return df[["Recipe", "Ingredients", "Instructions"]]


# ✅ Call the function to get the recipes DataFrame
recipes = load_recipes()


# ---------- Helper for unit conversion ----------
def convert_units(amount, from_unit, to_unit):
    """Convert between basic units (g↔kg, ml↔l)."""
    conversions = {
        ("g", "kg"): 1 / 1000,
        ("kg", "g"): 1000,
        ("ml", "l"): 1 / 1000,
        ("l", "ml"): 1000,
    }
    if from_unit == to_unit:
        return amount
    return amount * conversions.get((from_unit, to_unit), 1)


# ---------- Recipe matching ----------
def check_recipe_availability(recipe_ingredients, pantry_data):
    """Check how many ingredients from a recipe are available in the pantry."""
    ingredients = [x.strip() for x in str(recipe_ingredients).split(",") if x.strip()]
    total = len(ingredients)
    available_count = 0
    missing_items = []

    for item in ingredients:
        try:
            name_qty = item.split(":")
            name = name_qty[0].strip().lower()
            qty_unit = name_qty[1].strip() if len(name_qty) > 1 else ""
            qty = float("".join(filter(str.isdigit, qty_unit)) or 0)
            unit = "".join(filter(str.isalpha, qty_unit)) or "count"
        except (ValueError, IndexError, TypeError):
            name = item.lower().strip()
            qty = 0
            unit = "count"
        match = pantry_data[pantry_data["Product"] == name]
        if match.empty:
            missing_items.append(name)
            continue

        try:
            pantry_qty = float(match.iloc[0].get("Quantity", 0))
            pantry_unit = match.iloc[0].get("Unit", "count")

            converted_needed = convert_units(qty, unit, pantry_unit)
            if pantry_qty >= converted_needed:
                available_count += 1
            else:
                missing_items.append(name)

        except (ValueError, TypeError):
            # Catch invalid numeric or conversion issues
            missing_items.append(name)

    match_percentage = (available_count / total) * 100 if total > 0 else 0
    return match_percentage, missing_items


# ---------- Display results ----------
st.subheader(f"🥘 Personalized Recipe Matches for {username}")

results = []
for _, row in recipes.iterrows():
    match_percent, missing = check_recipe_availability(str(row["Ingredients"]), pantry)
    results.append(
        {
            "Recipe": row.get("Recipe", "Unnamed Recipe"),
            "Match %": round(match_percent, 1),
            "Missing": ", ".join(missing) if missing else "All available",
            "Instructions": row.get("Instructions", ""),
        }
    )

results_df = pd.DataFrame(results).sort_values(by="Match %", ascending=False)

if not results_df.empty:
    st.write("### 📋 Recipe Match Overview")
    st.dataframe(results_df[["Recipe", "Match %", "Missing"]], use_container_width=True)

    st.write("### 📖 Recipe Details")
    for _, row in results_df.iterrows():
        with st.expander(f"{row['Recipe']} — {row['Match %']}% match"):
            st.markdown(f"**✅ Available ingredients:** {row['Match %']}% match")
            st.markdown(f"**❌ Missing ingredients:** {row['Missing']}")
            st.markdown(f"**👩‍🍳 Instructions:** {row['Instructions']}")
else:
    st.info("No recipes could be matched with your pantry.")
