"""
recommended_recipes.py
Recommended Recipes Page for Smart Pantry Manager

Features:
- Personalized recipe suggestions based on user's pantry
- Match % calculation and missing ingredient hints
- Streamlit UI with expandable recipe details

Date: 2025-11-20
"""

import ast
import os
import re
import sqlite3
import unicodedata
from typing import List, Tuple

import pandas as pd
import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="Recommended Recipes", page_icon="🍳", layout="wide")

st.title("🍳 Recommended Recipes")
st.caption("Discover recipes you can cook with what's already in your pantry!")

# ---------- Check Username ----------
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please go to the Home page and enter your username first.")
    st.stop()

username = st.session_state["username"]
user_file = os.path.join(
    "smart_pantry_manager", "data", f"pantry_{username.replace(' ', '_').lower()}.xlsx"
)

# ---------- Load Pantry ----------
try:
    pantry_df = pd.read_excel(user_file)
    if "Product" in pantry_df.columns:
        pantry_df["Product"] = pantry_df["Product"].astype(str).str.lower().str.strip()
    else:
        pantry_df["Product"] = ""
except FileNotFoundError:
    st.info("Your pantry is empty. Please add items on the Home page.")
    st.stop()

# Remove duplicates and empty product names
pantry_products = sorted({p for p in pantry_df["Product"].tolist() if p and p.strip()})


# ---------- Load Recipes ----------
@st.cache_data
def load_recipes() -> pd.DataFrame:
    """
    Load recipes from SQLite and normalize columns.
    Returns DataFrame with Recipe, Ingredients, Instructions
    """
    db_path = os.path.join("smart_pantry_manager", "data", "Recipe_Dataset.sqlite")
    if not os.path.exists(db_path):
        st.error(
            "⚠️ Recipes database not found. Ensure Recipe_Dataset.sqlite "
            "is in smart_pantry_manager/data/."
        )
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM recipes", conn)
    except Exception as err:
        st.error(f"Error reading recipes: {err}")
        conn.close()
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])
    conn.close()

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    rename_map = {
        "title": "Recipe",
        "cleaned_ingredients": "Ingredients",
        "ingredient": "Ingredients",
        "instruction": "Instructions",
        "instructions": "Instructions",
    }
    df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True
    )
    # Ensure required columns exist
    for col in ["Recipe", "Ingredients", "Instructions"]:
        if col not in df.columns:
            df[col] = ""
    return df[["Recipe", "Ingredients", "Instructions"]]


recipes_df = load_recipes()
if recipes_df.empty:
    st.warning("No recipes available in the database.")
    st.stop()


# ---------- Utilities ----------
def normalize_text(s: str) -> str:
    """Normalize unicode artifacts and strip spaces."""
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\u200b-\u200f\u2028\u2029]", "", s)
    return s.strip()


def parse_ingredients(ingredients_str: str) -> List[str]:
    """Parse ingredients string into a cleaned list of ingredients."""
    if not ingredients_str:
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


def strip_leading_qty(s: str) -> str:
    """
    Remove leading quantity & units from ingredient to match pantry.
    Example: '1 cup milk' -> 'milk'
    """
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"^\s*\(?\d+(?:[\/\u00BC-\u00BE\u2150-\u215E]?\d*)?\)?\s*", "", s)
    s = re.sub(
        r"^\s*\d+(\.\d+)?\s*(cup|cups|tbsp|tbsp\.|tbsps|tsp|tsp\.|oz|lb|lbs|g|kg|ml|l)\b",
        "",
        s,
    )
    s = re.sub(r"^\s*(?:one|two|three|four|a|an)\s+", "", s)
    s = re.sub(r"^\s*\(?\d+[^a-zA-Z]*\)?\s*", "", s)
    s = re.sub(r"^[\-\–\—\s]+", "", s)
    return s.strip()


@st.cache_data
def cached_check_availability(
    recipe_ingredients: str, pantry_products_tuple: Tuple[str, ...]
) -> Tuple[float, List[str]]:
    """
    Return (match_percent, missing_items_list) using whole-word matching.
    """
    ingredients = parse_ingredients(recipe_ingredients)
    if not ingredients:
        return 0.0, []

    total = len(ingredients)
    available_count = 0
    missing_items = []

    regexes = [
        re.compile(rf"\b{re.escape(p)}\b", flags=re.IGNORECASE)
        for p in pantry_products_tuple
    ]

    for item in ingredients:
        item_norm = normalize_text(item).lower()
        name_candidate = strip_leading_qty(item_norm)
        text_to_search = name_candidate or item_norm
        matched = any(rx.search(text_to_search) for rx in regexes)
        if matched:
            available_count += 1
        else:
            words = text_to_search.split()
            short = " ".join(words[-3:] if len(words) > 3 else words)
            missing_items.append(short)

    match_percentage = (available_count / total) * 100 if total else 0.0
    return round(match_percentage, 1), missing_items


# ---------- UI: Filters ----------
st.subheader(f"🥘 Personalized Recipe Matches for {username}")

col1, col2 = st.columns(2)
with col1:
    min_match = st.slider("Minimum match percentage:", 0, 100, 50, 5)
with col2:
    max_recipes = st.number_input("Maximum recipes to show:", 10, 200, 20, 5)

st.write("🔍 Analyzing recipes...")
progress_bar = st.progress(0)
status_text = st.empty()

results = []
total_recipes = len(recipes_df)
pantry_key = tuple(pantry_products)

for idx, (_, row) in enumerate(recipes_df.iterrows()):
    progress_bar.progress((idx + 1) / total_recipes)
    status_text.text(f"Processing recipe {idx + 1} of {total_recipes}...")
    ingredients_raw = normalize_text(row.get("Ingredients") or "")
    match_percent, missing = cached_check_availability(ingredients_raw, pantry_key)
    if match_percent >= min_match:
        instr = normalize_text(row.get("Instructions") or "")
        instr_preview = instr[:500] + "..." if len(instr) > 500 else instr
        results.append(
            {
                "Recipe": row.get("Recipe") or "Unnamed Recipe",
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

# Sort and limit results
results_df = pd.DataFrame(results)
if not results_df.empty:
    results_df = results_df.sort_values(by="Match %", ascending=False)
    results_df = results_df.head(int(max_recipes))
    st.success(f"✅ Found {len(results_df)} matching recipes!")

    st.write("### 📋 Recipe Match Overview")
    st.dataframe(
        results_df[["Recipe", "Match %", "Missing"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

    st.write("### 📖 Recipe Details")
    for _, row in results_df.iterrows():
        match_color = (
            "🟢" if row["Match %"] >= 80 else "🟡" if row["Match %"] >= 60 else "🟠"
        )
        with st.expander(f"{match_color} {row['Recipe']} — {row['Match %']}% match"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"**Match:** {row['Match %']}%")
                st.markdown(f"**Missing:** {row['Missing']}")
            ing_list = parse_ingredients(row["Ingredients"] or "")
            with c2:
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
    st.info(
        f"No recipes found with at least {min_match}% match. "
        "Try lowering the minimum match percentage."
    )
