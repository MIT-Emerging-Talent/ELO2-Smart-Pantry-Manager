"""
all_recipes.py
All Recipes Page for Smart Pantry Application (SQLite version)

Features:
- Load recipes from SQLite database
- Display recipe list with ingredients and instructions
- Supports search/filtering

Date: 2025-11-20
"""

import ast
import os
import sqlite3

import pandas as pd
import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="All Recipes", page_icon="📜", layout="wide")

st.title("📜 All Recipes")
st.caption("Browse all available recipes in the Smart Pantry system.")


# ---------- Load Recipes ----------
@st.cache_data
def load_recipes() -> pd.DataFrame:
    """
    Load recipes from SQLite database and normalize column names.

    Returns:
        pd.DataFrame: Columns = Recipe, Ingredients, Instructions
    """
    db_path = "smart_pantry_manager/data/Recipe_Dataset.sqlite"
    if not os.path.exists(db_path):
        st.error(f"❌ Database file not found at: {db_path}")
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM recipes", conn)
    except Exception as err:
        st.error(f"Error reading database: {err}")
        conn.close()
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])
    conn.close()

    # Normalize column names
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

    # Keep only required columns
    required_cols = ["Recipe", "Ingredients", "Instructions"]
    df = df[[col for col in required_cols if col in df.columns]]
    return df


def format_ingredients(ingredients_str: str) -> list:
    """
    Convert ingredients string into a list.

    Args:
        ingredients_str (str): String representation of ingredients

    Returns:
        list: List of ingredients as strings
    """
    if not ingredients_str:
        return []

    s = ingredients_str.strip()
    try:
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [str(x).strip() for x in parsed if str(x).strip()]
        if "," in s:
            return [item.strip() for item in s.split(",") if item.strip()]
        return [s]
    except Exception:
        # fallback for | or newline-separated strings
        if "|" in s:
            return [x.strip() for x in s.split("|") if x.strip()]
        if "\n" in s:
            return [x.strip() for x in s.split("\n") if x.strip()]
        return [s]


recipes_df = load_recipes()

# ---------- Display Recipes ----------
if recipes_df.empty:
    st.info("No recipes found.")
else:
    search_term = st.text_input("🔍 Search for a recipe:")
    filtered_df = (
        recipes_df[recipes_df["Recipe"].str.contains(search_term, case=False, na=False)]
        if search_term
        else recipes_df
    )

    for _, row in filtered_df.iterrows():
        with st.expander(f"📖 {row['Recipe']}"):
            st.markdown("**🧂 Ingredients:**")
            ing_list = format_ingredients(row.get("Ingredients") or "")
            for ing in ing_list:
                st.write(f"• {ing}")

            st.markdown("**👩‍🍳 Instructions:**")
            st.write(row.get("Instructions") or "No instructions available.")
