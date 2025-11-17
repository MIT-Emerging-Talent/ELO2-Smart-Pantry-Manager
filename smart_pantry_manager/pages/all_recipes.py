# spell-checker: disable
"""
All Recipes Page for Smart Pantry Application (SQLite version)
"""

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
    db_path = "the_app/data/Recipe_Dataset.sqlite"

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)

    # Load the table "recipes"
    df = pd.read_sql_query("SELECT * FROM recipes", conn)

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
        with st.expander(row["Recipe"]):
            st.markdown(f"**🧂 Ingredients:** {row['Ingredients']}")
            st.markdown(f"**👩‍🍳 Instructions:** {row['Instructions']}")
