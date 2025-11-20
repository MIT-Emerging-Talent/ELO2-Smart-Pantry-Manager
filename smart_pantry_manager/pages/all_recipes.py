# spell-checker: disable
"""
All Recipes Page for Smart Pantry Manager (SQLite version)
Shows all recipes with diet type info.
"""

import ast
import os
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="All Recipes", page_icon="📜", layout="wide")
st.title("📜 All Recipes")
st.caption("Browse all recipes and see diet type (Vegan/Vegetarian/Non-Vegetarian)")


# ---------- Load recipes ----------
@st.cache_data
def load_recipes():
    db_path = "smart_pantry_manager/data/cleaned_data.sqlite"
    if not os.path.exists(db_path):
        st.error("⚠️ Recipes database not found.")
        return pd.DataFrame(
            columns=["Recipe", "Ingredients", "Instructions", "Diet_type"]
        )
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM all_recipes", conn)
    except Exception as e:
        st.error(f"Error reading recipes: {e}")
        conn.close()
        return pd.DataFrame(
            columns=["Recipe", "Ingredients", "Instructions", "Diet_type"]
        )
    conn.close()
    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    df.rename(
        columns={
            "title": "Recipe",
            "instruction": "Instructions",
            "instructions": "Instructions",
            "diet_type": "Diet_type",
            "ingredient": "Ingredients",
            "cleaned_ingredients": "Ingredients",
        },
        inplace=True,
    )
    for col in ["Recipe", "Ingredients", "Instructions", "Diet_type"]:
        if col not in df.columns:
            df[col] = ""
    return df[["Recipe", "Ingredients", "Instructions", "Diet_type"]]


def parse_ingredients(ingredients_str):
    if not ingredients_str:
        return []
    s = str(ingredients_str)
    try:
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            return [str(x).strip() for x in parsed if str(x).strip()]
        if "," in s:
            return [x.strip() for x in s.split(",") if x.strip()]
        return [s]
    except:
        return [s]


recipes = load_recipes()
if recipes.empty:
    st.info("No recipes found.")
    st.stop()

search = st.text_input("🔍 Search for a recipe:")
filtered = (
    recipes[recipes["Recipe"].str.contains(search, case=False, na=False)]
    if search
    else recipes
)

for _, row in filtered.iterrows():
    diet = row.get("Diet_type", "Unknown").capitalize()
    recipe_name = row.get("Recipe", "Unnamed Recipe")
    with st.expander(f"📖 {recipe_name} — {diet}"):
        st.markdown(f"**Diet Type:** {diet}")
        st.markdown("**🧂 Ingredients:**")
        ing_list = parse_ingredients(row["Ingredients"])
        if ing_list:
            for ing in ing_list:
                st.write(f"• {ing}")
        else:
            st.write("No ingredient data available.")
        st.markdown("**👩‍🍳 Instructions:**")
        st.write(row["Instructions"] or "No instructions available.")
