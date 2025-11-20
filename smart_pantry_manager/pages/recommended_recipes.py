# spell-checker: disable
"""
Recommended Recipes Page
Shows recipes matched with user's pantry, including diet type
"""

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
st.caption("Discover recipes you can cook with what's already in your pantry!")

# ---------- Check Username ----------
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please go to Home page and enter your username first.")
    st.stop()

username = st.session_state["username"]
USER_FILE = os.path.join(
    "smart_pantry_manager", "data", f"pantry_{username.replace(' ', '_').lower()}.xlsx"
)

try:
    pantry = pd.read_excel(USER_FILE)
    if "Product" in pantry.columns:
        pantry["Product"] = pantry["Product"].astype(str).str.lower().str.strip()
    else:
        pantry["Product"] = ""
except FileNotFoundError:
    st.info("Your pantry is empty. Add items on Home page first.")
    st.stop()

pantry_products = sorted({p for p in pantry["Product"].tolist() if p and p.strip()})
pantry_regexes = [
    re.compile(rf"\b{re.escape(p)}\b", flags=re.IGNORECASE) for p in pantry_products
]

# ---------- Load Recipes ----------
DB_PATH = os.path.join("smart_pantry_manager", "data", "cleaned_data.sqlite")


@st.cache_data
def load_recipes():
    if not os.path.exists(DB_PATH):
        st.error("Recipes database not found.")
        return pd.DataFrame(
            columns=["Title", "Ingredients", "Instructions", "Diet_Type"]
        )
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM all_recipes", conn)
    except Exception as e:
        st.error(f"Error reading recipes: {e}")
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
    st.info("No recipes available in DB.")
    st.stop()


# ---------- Utilities ----------
def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\u200b-\u200f\u2028\u2029]", "", s)
    return s.strip()


def parse_ingredients(ingredients_str: str) -> List[str]:
    if not ingredients_str:
        return []
    s = normalize_text(str(ingredients_str))
    try:
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            return [normalize_text(str(x)) for x in parsed if str(x).strip()]
        if "," in s:
            return [normalize_text(x) for x in s.split(",") if x.strip()]
        return [s]
    except Exception:
        return [s]


def strip_leading_qty(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"^\s*\(?\d+(?:[\/\u00BC-\u00BE\u2150-\u215E]?\d*)?\)?\s*", "", s)
    s = re.sub(
        r"^\s*\d+(\.\d+)?\s*(cup|cups|tbsp|tbsp.|tbsps|tsp|tsp.|oz|lb|lbs|g|kg|ml|l)\b",
        "",
        s,
    )
    s = re.sub(r"^\s*(?:one|two|three|four|a|an)\s+", "", s)
    s = re.sub(r"^[\-\–\—\s]+", "", s)
    return s.strip()


@st.cache_data
def cached_check_availability(
    recipe_ingredients: str, pantry_products_tuple: Tuple[str, ...]
):
    ingredients = parse_ingredients(recipe_ingredients)
    if not ingredients:
        return 0.0, []
    total = len(ingredients)
    available_count = 0
    missing_items = []
    regexes = [
        re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in pantry_products_tuple
    ]
    for item in ingredients:
        item_norm = normalize_text(str(item)).lower()
        name_candidate = strip_leading_qty(item_norm)
        text_to_search = name_candidate or item_norm
        matched = any(rx.search(text_to_search) for rx in regexes)
        if matched:
            available_count += 1
        else:
            words = text_to_search.split()
            short = " ".join(words[-3:] if len(words) > 3 else words)
            missing_items.append(short)
    match_percentage = (available_count / total) * 100 if total > 0 else 0.0
    return round(match_percentage, 1), missing_items


# ---------- Filters ----------
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
total_recipes = len(recipes)
pantry_key = tuple(pantry_products)

for idx, (_, row) in enumerate(recipes.iterrows()):
    progress_bar.progress((idx + 1) / total_recipes)
    status_text.text(f"Processing recipe {idx + 1} of {total_recipes}...")
    ingredients_raw = normalize_text(str(row.get("Ingredients", "")))
    match_percent, missing = cached_check_availability(ingredients_raw, pantry_key)
    if match_percent >= min_match:
        instr = normalize_text(str(row.get("Instructions", "")))
        instr_preview = instr[:500] + "..." if len(instr) > 500 else instr
        results.append(
            {
                "Title": row.get("Title", "Unnamed Recipe"),
                "Diet_Type": row.get("Diet_Type", "Unknown"),
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
    results_df = results_df.sort_values("Match %", ascending=False).head(
        int(max_recipes)
    )
    st.success(f"✅ Found {len(results_df)} matching recipes!")
    st.write("### 📋 Recipe Match Overview")
    st.dataframe(
        results_df[["Title", "Diet_Type", "Match %", "Missing"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )
    st.write("### 📖 Recipe Details")
    for _, row in results_df.iterrows():
        match_color = (
            "🟢" if row["Match %"] >= 80 else "🟡" if row["Match %"] >= 60 else "🟠"
        )
        with st.expander(f"{row['Title']} — {row['Diet_Type']} {match_color}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Match:** {row['Match %']}%")
                st.markdown(f"**Missing:** {row['Missing']}")
            ing_list = parse_ingredients(row["Ingredients"])
            with col2:
                st.markdown("**🧂 Ingredients:**")
                for ing in ing_list[:10]:
                    st.write(f"• {ing}")
                if len(ing_list) > 10:
                    st.write(f"*...and {len(ing_list) - 10} more*")
                st.markdown("**👩‍🍳 Instructions:**")
                st.write(row["Instructions"] or "No instructions available.")
else:
    st.info(f"No recipes found with at least {min_match}% match.")
