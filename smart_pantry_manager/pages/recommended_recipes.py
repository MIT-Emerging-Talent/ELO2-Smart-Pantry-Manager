# spell-checker: disable
"""
Recommended Recipes Page
Shows personalized matches with diet type info.
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
st.caption("Discover recipes you can cook with what's in your pantry!")

if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please enter your username on the Home page first.")
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
    st.info("Your pantry is empty. Add items on Home page.")
    st.stop()

pantry_products = sorted({p for p in pantry["Product"].tolist() if p.strip()})


# ---------- Load Recipes ----------
@st.cache_data
def load_recipes() -> pd.DataFrame:
    db_path = "smart_pantry_manager/data/cleaned_data.sqlite"
    if not os.path.exists(db_path):
        st.error("Recipes DB not found.")
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
    df.columns = [c.strip().lower() for c in df.columns]
    df.rename(
        columns={
            "title": "Recipe",
            "ingredient": "Ingredients",
            "cleaned_ingredients": "Ingredients",
            "instruction": "Instructions",
            "instructions": "Instructions",
            "diet_type": "Diet_type",
        },
        inplace=True,
    )
    for col in ["Recipe", "Ingredients", "Instructions", "Diet_type"]:
        if col not in df.columns:
            df[col] = ""
    return df[["Recipe", "Ingredients", "Instructions", "Diet_type"]]


recipes = load_recipes()
if recipes.empty:
    st.warning("No recipes available.")
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
    s = normalize_text(ingredients_str)
    try:
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            return [normalize_text(str(x)) for x in parsed if str(x).strip()]
        if "," in s:
            return [normalize_text(x) for x in s.split(",") if x.strip()]
        return [s]
    except:
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
    s = re.sub(r"^\s*\(?\d+[^a-zA-Z]*\)?\s*", "", s)
    s = re.sub(r"^[\-\–\—\s]+", "", s)
    return s.strip()


@st.cache_data
def cached_check_availability(
    recipe_ingredients: str, pantry_products_tuple: Tuple[str, ...]
) -> Tuple[float, List[str]]:
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
        text_to_search = strip_leading_qty(item_norm) or item_norm
        matched = any(rx.search(text_to_search) for rx in regexes)
        if matched:
            available_count += 1
        else:
            words = text_to_search.split()
            short = " ".join(words[-3:] if len(words) > 3 else words)
            missing_items.append(short)
    match_percentage = (available_count / total) * 100 if total > 0 else 0.0
    return round(match_percentage, 1), missing_items


# ---------- UI: Filters & Analysis ----------
st.subheader(f"🥘 Personalized Recipe Matches for {username}")
col1, col2 = st.columns(2)
with col1:
    min_match = st.slider("Minimum match percentage:", 0, 100, 50, 5)
with col2:
    max_recipes = st.number_input("Maximum recipes to show:", 10, 200, 20, 5)

# ✅ Progress Bar & Status
progress_bar = st.progress(0)
status_text = st.empty()

# 📦 Pantry preview
st.expander("📦 Your Pantry Preview", expanded=False).write(
    pantry[["Product", "Quantity", "Unit", "Days Left"]]
)

st.write("🔍 Analyzing recipes...")
results = []
total_recipes = len(recipes)
pantry_key = tuple(pantry_products)

for idx, (_, row) in enumerate(recipes.iterrows()):
    progress = (idx + 1) / total_recipes
    progress_bar.progress(progress)
    status_text.text(f"Processing recipe {idx + 1} of {total_recipes}...")
    ingredients_raw = normalize_text(row.get("Ingredients") or "")
    match_percent, missing = cached_check_availability(ingredients_raw, pantry_key)
    if match_percent >= min_match:
        instr = normalize_text(row.get("Instructions") or "")
        instr_preview = instr[:500] + "..." if len(instr) > 500 else instr
        results.append(
            {
                "Recipe": row.get("Recipe") or "Unnamed Recipe",
                "Diet_type": row.get("Diet_type") or "Unknown",
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
        results_df[["Recipe", "Diet_type", "Match %", "Missing"]].reset_index(
            drop=True
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.write("### 📖 Recipe Details")
    for _, row in results_df.iterrows():
        diet = row["Diet_type"].capitalize()
        match_color = (
            "🟢" if row["Match %"] >= 80 else "🟡" if row["Match %"] >= 60 else "🟠"
        )
        recipe_name = row["Recipe"]
        with st.expander(
            f"{match_color} {recipe_name} — {diet} — {row['Match %']}% match"
        ):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Diet Type:** {diet}")
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
    st.info(
        f"No recipes found with at least {min_match}% match. Try lowering the filter."
    )
