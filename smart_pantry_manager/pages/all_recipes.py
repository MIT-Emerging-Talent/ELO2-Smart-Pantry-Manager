# spell-checker: disable
"""
All Recipes Page for Smart Pantry Application
"""

import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="All Recipes", page_icon="📜", layout="wide")

st.title("📜 All Recipes")
st.caption("Browse all available recipes in the Smart Pantry system.")


# ---------- Load recipes (CSV) ----------
@st.cache_data
def load_recipes():
    """Load recipes from CSV and clean up column names."""
    csv_path = os.path.join("the_app", "data", "Recipe_Dataset.csv")
    df = pd.read_csv(csv_path, index_col=0)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename columns if they exist
    if "title" in df.columns:
        df.rename(columns={"title": "Recipe"}, inplace=True)
    if "cleaned_ingredients" in df.columns:
        df.rename(columns={"cleaned_ingredients": "Ingredients"}, inplace=True)
    if "instruction" in df.columns:
        df.rename(columns={"instruction": "Instructions"}, inplace=True)
    elif "instructions" in df.columns:
        df.rename(columns={"instructions": "Instructions"}, inplace=True)

    # Only return required columns
    required_cols = ["Recipe", "Ingredients", "Instructions"]
    df = df[[col for col in required_cols if col in df.columns]]

    return df


recipes = load_recipes()

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
