# spell-checker: disable
"""
All Recipes Page
Shows all recipes and diet type from cleaned_data.sqlite
Now includes:
- Diet Type Filter
- Pagination (20 recipes per page)
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

    for col in ["Title", "Ingredients", "Instructions", "Diet_Type"]:
        if col not in df.columns:
            df[col] = ""

    return df


recipes = load_recipes()
if recipes.empty:
    st.info("No recipes found.")
    st.stop()


# ---------------- Filter by Diet Type ----------------
all_diets = ["All"] + sorted(list(recipes["Diet_Type"].dropna().unique()))
selected_diet = st.selectbox("🥗 Filter by Diet Type:", all_diets)

if selected_diet != "All":
    recipes = recipes[recipes["Diet_Type"] == selected_diet]


# ---------- Search Recipes ----------
search_query = st.text_input("🔍 Search recipes by title:", "")
if search_query:
    recipes = recipes[recipes["Title"].str.contains(search_query, case=False, na=False)]

if recipes.empty:
    st.info("No recipes match your filters.")
    st.stop()


# ---------- Pagination (20 per page) ----------
RECIPES_PER_PAGE = 20
total_pages = (len(recipes) - 1) // RECIPES_PER_PAGE + 1

page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)

start_idx = (page - 1) * RECIPES_PER_PAGE
end_idx = start_idx + RECIPES_PER_PAGE

recipes_page = recipes.iloc[start_idx:end_idx]


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
for _, row in recipes_page.iterrows():
    title = str(row.get("Title", "Unnamed Recipe"))
    diet = str(row.get("Diet_Type", "Unknown"))

    with st.expander(f"📖 {title} — {diet}"):
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"**Diet Type:** {diet}")

        with col2:
            st.markdown("**🧂 Ingredients:**")
            ing_list = parse_ingredients(row.get("Ingredients", ""))
            if ing_list:
                for ing in ing_list:
                    st.write(f"• {ing}")
            else:
                st.write("No ingredient data available.")

            st.markdown("**👩‍🍳 Instructions:**")

        st.write(str(row.get("Instructions", "No instructions available.")))
