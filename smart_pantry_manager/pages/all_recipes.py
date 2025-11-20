# spell-checker: disable
"""
All Recipes Page for Smart Pantry Application (SQLite version)
"""

import ast
import os
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="All Recipes", page_icon="📜", layout="wide")

st.title("📜 All Recipes")
st.caption("Browse all available recipes in the Smart Pantry system.")


# ---------- Load recipes from SQLite ----------
@st.cache_data
def load_recipes():
    """
    Load recipes from the SQLite database and normalize column names.
    Returns a DataFrame with columns: Recipe, Ingredients, Instructions
    """
    db_path = "smart_pantry_manager/data/Recipe_Dataset.sqlite"

    # Check if database file exists
    if not os.path.exists(db_path):
        st.error(f"❌ Database file not found at: {db_path}")
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)

    try:
        # Load the table "recipes"
        df = pd.read_sql_query("SELECT * FROM recipes", conn)
    except Exception as e:
        st.error(f"Error reading database: {e}")
        conn.close()
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])

    conn.close()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename columns if they exist
    rename_map = {
        "title": "Recipe",
        "cleaned_ingredients": "Ingredients",
        "instruction": "Instructions",
        "instructions": "Instructions",
    }
    df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True
    )

    # Keep only required columns
    required_cols = ["Recipe", "Ingredients", "Instructions"]
    df = df[[col for col in required_cols if col in df.columns]]

    return df


def format_ingredients(ingredients_str):
    """
    Convert ingredients from string representation of list to a Python list.
    """
    try:
        # Try to parse as a Python list
        if ingredients_str.startswith("["):
            return ast.literal_eval(ingredients_str)
        # If it's comma-separated
        elif "," in ingredients_str:
            return [item.strip() for item in ingredients_str.split(",")]
        else:
            return [ingredients_str]
    except:
        # If parsing fails, return as single item list
        return [ingredients_str]


recipes = load_recipes()

# ---------- Display recipes ----------
if recipes.empty:
    st.info("No recipes found.")
else:
    search = st.text_input("🔍 Search for a recipe:")
    filtered = (
        recipes[recipes["Recipe"].str.contains(search, case=False, na=False)]
        if search
        else recipes
    )

    for _, row in filtered.iterrows():
        with st.expander(f"📖 {row['Recipe']}"):
            st.markdown("**🧂 Ingredients:**")
            ingredients_list = format_ingredients(row["Ingredients"])
            for ingredient in ingredients_list:
                st.write(f"• {ingredient}")

            st.markdown("**👩‍🍳 Instructions:**")
            st.write(row["Instructions"])
