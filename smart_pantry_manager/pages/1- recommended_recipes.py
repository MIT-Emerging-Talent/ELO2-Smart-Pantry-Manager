# recommended_recipes.py
# Optimized Recommended Recipes page with ingredient selection and diet filter
# Date: 2025-11-20

import ast
import os
import re
import sqlite3
import unicodedata
from typing import List, Tuple

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Recommended Recipes", page_icon="🍳", layout="wide")

st.title("🍳 Recommended Recipes")
st.caption("Discover recipes you can cook with your selected ingredients!")

# ---------- Check username ----------
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please go to Home page and enter your username first.")
    st.stop()

username = st.session_state["username"]
USER_FILE = os.path.join(
    "smart_pantry_manager",
    "data",
    "user_data",
    f"pantry_{username.replace(' ', '_').lower()}.xlsx",
)

# ---------- Load pantry ----------
try:
    pantry = pd.read_excel(USER_FILE)
    pantry_products = sorted({p.lower().strip() for p in pantry.get("Product", [])})
except FileNotFoundError:
    st.info("Your pantry is empty. Add items on Home page first.")
    st.stop()

# ---------- User ingredient selection ----------
st.sidebar.header("Select Ingredients to Use")
selected_ingredients = st.sidebar.multiselect(
    "Choose ingredients:", options=pantry_products, default=pantry_products
)

st.sidebar.header("Select Diet Type")
selected_diet = st.sidebar.selectbox(
    "Diet preference:", ["Any", "Vegan", "Vegetarian", "Non-Vegetarian"]
)


# ---------- Load recipes ----------
@st.cache_data
def load_recipes() -> pd.DataFrame:
    db_path = os.path.join("smart_pantry_manager", "data", "cleaned_data.sqlite")
    if not os.path.exists(db_path):
        st.error("Recipes database not found! Place cleaned_data.sqlite in data/.")
        return pd.DataFrame(
            columns=["Title", "Ingredients", "Instructions", "Diet_Type"]
        )
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM all_recipes", conn)
    except Exception as e:
        conn.close()
        st.error(f"Error loading recipes: {e}")
        return pd.DataFrame(
            columns=["Title", "Ingredients", "Instructions", "Diet_Type"]
        )
    conn.close()
    for col in ["Title", "Ingredients", "Instructions", "Diet_Type"]:
        if col not in df.columns:
            df[col] = ""
    return df[["Title", "Ingredients", "Instructions", "Diet_Type"]]


recipes = load_recipes()
if recipes.empty:
    st.warning("No recipes found in the database.")
    st.stop()


# ---------- Utilities ----------
def normalize_text(s: str) -> str:
    """Normalize unicode artifacts and strip."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\u200b-\u200f\u2028\u2029]", "", s)
    return s.strip()


def parse_ingredients(ingredients_str: str) -> List[str]:
    """Parse ingredients stored as list string or comma-separated."""
    if pd.isna(ingredients_str):
        return []
    s = normalize_text(ingredients_str)
    try:
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [normalize_text(str(x)) for x in parsed if str(x).strip()]
        if "," in s:
            return [normalize_text(x) for x in s.split(",") if x.strip()]
        return [s]
    except Exception:
        if "|" in s:
            return [normalize_text(x) for x in s.split("|") if x.strip()]
        if "\n" in s:
            return [normalize_text(x) for x in s.split("\n") if x.strip()]
        return [s]


def clean_ingredient_name(s: str) -> str:
    """Extract core ingredient name for matching."""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"\d+[\/\d\s]*\s*(cup|cups|tbsp|tsp|oz|lb|lbs|g|kg|ml|l)?", "", s)
    s = re.sub(r"[^a-zA-Z\u00C0-\u017F\s]+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


@st.cache_data
def cached_check_availability(
    recipe_ingredients: str, selected_tuple: Tuple[str, ...]
) -> Tuple[float, List[str]]:
    """Return match % and missing items for selected ingredients."""
    ingredients = parse_ingredients(recipe_ingredients)
    if not ingredients:
        return 0.0, []

    total = len(ingredients)
    available_count = 0
    missing_items = []
    regexes = [
        re.compile(rf"\b{re.escape(p)}\b", flags=re.IGNORECASE) for p in selected_tuple
    ]

    for item in ingredients:
        core_name = clean_ingredient_name(item)
        text_to_search = core_name or item
        matched = any(rx.search(text_to_search) for rx in regexes)
        if matched:
            available_count += 1
        else:
            missing_items.append(core_name)
    match_percent = (available_count / total) * 100 if total else 0.0
    return round(match_percent, 1), missing_items


# ---------- Filters ----------
st.subheader(f"🥘 Personalized Recipes for {username}")

min_match = st.slider("Minimum match %:", 0, 100, 50, 5)
max_recipes = st.number_input("Max recipes to show:", 10, 200, 20, 5)

st.write("🔍 Analyzing recipes...")
progress_bar = st.progress(0)
status_text = st.empty()
results = []
total_recipes = len(recipes)
selected_tuple = tuple(selected_ingredients)

for idx, (_, row) in enumerate(recipes.iterrows()):
    progress = (idx + 1) / total_recipes
    progress_bar.progress(progress)
    status_text.text(f"Processing recipe {idx + 1} of {total_recipes}...")

    if selected_diet != "Any" and row["Diet_Type"].strip() != selected_diet:
        continue

    ingredients_raw = row.get("Ingredients") or ""
    match_percent, missing = cached_check_availability(ingredients_raw, selected_tuple)

    if match_percent >= min_match:
        instr = normalize_text(row.get("Instructions") or "")
        instr_preview = instr  # show full instructions
        diet = row.get("Diet_Type") or "Unknown"
        results.append(
            {
                "Recipe": row.get("Title") or "Unnamed Recipe",
                "Diet": diet,
                "Match %": match_percent,
                "Missing": ", ".join(missing[:3]) + ("..." if len(missing) > 3 else "")
                if missing
                else "✅ All available",
                "Instructions": instr_preview,
                "Ingredients": ingredients_raw,
            }
        )

progress_bar.empty()
status_text.empty()
results_df = pd.DataFrame(results)
if not results_df.empty:
    results_df = results_df.sort_values(by="Match %", ascending=False).head(
        int(max_recipes)
    )
    st.success(f"✅ Found {len(results_df)} matching recipes!")

    st.write("### 📋 Recipe Match Overview")
    st.dataframe(
        results_df[["Recipe", "Diet", "Match %", "Missing"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.write("### 📖 Recipe Details")
    for _, row in results_df.iterrows():
        match_color = (
            "🟢" if row["Match %"] >= 80 else "🟡" if row["Match %"] >= 60 else "🟠"
        )
        with st.expander(f"{match_color} {row['Recipe']} - {row['Diet']}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Match:** {row['Match %']}%")
                st.markdown(f"**Missing:** {row['Missing']}")
            ing_list = parse_ingredients(row["Ingredients"] or "")
            with col2:
                st.markdown("**🧂 Ingredients:**")
                if ing_list:
                    for ing in ing_list[:10]:
                        st.write(f"• {ing}")
                    if len(ing_list) > 10:
                        st.write(f"*...and {len(ing_list) - 10} more*")
                else:
                    st.write("No ingredient data available.")
            st.markdown("**👩‍🍳 Instructions:**")
            st.write(row["Instructions"] or "No instructions available.")
else:
    st.info(f"No recipes found with at least {min_match}% match.")
