# spell-checker: disable
"""
All Recipes Page
Shows all recipes and diet type from cleaned_data.sqlite
"""

import ast
import os
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="All Recipes", page_icon="📜", layout="wide")
st.title("📜 All Recipes")
st.caption("Browse all recipes with diet type from Smart Pantry DB.")

DB_PATH = os.path.join("smart_pantry_manager", "data", "cleaned_data.sqlite")


# ---------- Load Recipes ----------
@st.cache_data
def load_recipes():
    if not os.path.exists(DB_PATH):
        st.error("❌ Recipes database not found.")
        return pd.DataFrame(
            columns=["Title", "Ingredients", "Instructions", "Diet_Type"]
        )
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM all_recipes", conn)
    except Exception as e:
        st.error(f"Error loading recipes: {e}")
        conn.close()
        return pd.DataFrame(
            columns=["Title", "Ingredients", "Instructions", "Diet_Type"]
        )
    conn.close()
    # Ensure required columns exist
    for col in ["Title", "Ingredients", "Instructions", "Diet_Type"]:
        if col not in df.columns:
            df[col] = ""
    return df


recipes = load_recipes()
if recipes.empty:
    st.info("No recipes found.")
    st.stop()


# ---------- Parse Ingredients ----------
def parse_ingredients(ingredients_str):
    if pd.isna(ingredients_str):
        return []
    try:
        if ingredients_str.startswith("[") and ingredients_str.endswith("]"):
            parsed = ast.literal_eval(ingredients_str)
            return [str(x).strip() for x in parsed if str(x).strip()]
        elif "," in ingredients_str:
            return [x.strip() for x in ingredients_str.split(",") if x.strip()]
        else:
            return [ingredients_str]
    except Exception:
        return [ingredients_str]


# ---------- Display Recipes ----------
for _, row in recipes.iterrows():
    title = str(row.get("Title", "Unnamed Recipe"))
    diet = str(row.get("Diet_Type", "Unknown"))
    with st.expander(f"📖 {title} — {diet}"):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**Diet Type:** {diet}")
        with col2:
            st.markdown("**🧂 Ingredients:**")
            ing_list = parse_ingredients(row.get("Ingredients", ""))
            for ing in ing_list[:10]:
                st.write(f"• {ing}")
            if len(ing_list) > 10:
                st.write(f"*...and {len(ing_list) - 10} more*")
            st.markdown("**👩‍🍳 Instructions:**")
            st.write(str(row.get("Instructions", "No instructions available.")))
