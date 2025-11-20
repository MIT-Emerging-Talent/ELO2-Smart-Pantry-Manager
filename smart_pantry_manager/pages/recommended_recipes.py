# recommended_recipes.py
# Optimized Recommended Recipes page for Smart Pantry Manager
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
st.caption("Discover recipes you can cook with what's already in your pantry!")

# ---------- Check username ----------
if "username" not in st.session_state or not st.session_state["username"]:
    st.warning("Please go to the Home page and enter your username first.")
    st.stop()

username = st.session_state["username"]
USER_FILE = os.path.join(
    "smart_pantry_manager", "data", f"pantry_{username.replace(' ', '_').lower()}.xlsx"
)

# ---------- Load pantry ----------
try:
    pantry = pd.read_excel(USER_FILE)
    # Normalize pantry product names
    if "Product" in pantry.columns:
        pantry["Product"] = pantry["Product"].astype(str).str.lower().str.strip()
    else:
        pantry["Product"] = ""
except FileNotFoundError:
    st.info("Your pantry is empty. Please add items on the Home page.")
    st.stop()

# remove duplicates and empty
pantry_products = sorted({p for p in pantry["Product"].tolist() if p and p.strip()})

# Build compiled regex patterns for strict whole-word matching
# e.g., pantry 'milk' -> regex '\bmilk\b' (case-insensitive)
pantry_regexes = [
    re.compile(rf"\b{re.escape(prod)}\b", flags=re.IGNORECASE)
    for prod in pantry_products
]


# ---------- Load recipes ----------
@st.cache_data
def load_recipes() -> pd.DataFrame:
    db_path = os.path.join("smart_pantry_manager", "data", "Recipe_Dataset.sqlite")
    if not os.path.exists(db_path):
        st.error(
            "⚠️ Recipes database not found. Please ensure Recipe_Dataset.sqlite is in smart_pantry_manager/data/."
        )
        return pd.DataFrame(columns=["Recipe", "Ingredients", "Instructions"])
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM recipes", conn)
    except Exception as e:
        st.error(f"Error reading recipes: {e}")
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
    required_cols = ["Recipe", "Ingredients", "Instructions"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    # Keep required only
    return df[required_cols]


recipes = load_recipes()

if recipes.empty:
    st.warning("No recipes available in the database.")
    st.stop()


# ---------- Utilities ----------
def normalize_text(s: str) -> str:
    """Normalize unicode artifacts and strip."""
    if s is None:
        return ""
    # fix weird combined characters from windows-1252/utf-8 issues
    s = str(s)
    s = unicodedata.normalize("NFKC", s)
    # remove zero-width and weird control chars
    s = re.sub(r"[\u200b-\u200f\u2028\u2029]", "", s)
    return s.strip()


def parse_ingredients(ingredients_str: str) -> List[str]:
    """Parse ingredients stored as a Python list string into a list of cleaned ingredient strings."""
    if not ingredients_str:
        return []
    s = normalize_text(ingredients_str)
    try:
        # likely a list literal like "['1 cup milk', 'salt']"
        if s.startswith("[") and s.endswith("]"):
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [normalize_text(str(x)) for x in parsed if str(x).strip()]
        # fallback: comma-separated
        if "," in s:
            return [normalize_text(item) for item in s.split(",") if item.strip()]
        return [s]
    except Exception:
        # last-resort: try splitting by '|' or newline
        if "|" in s:
            return [normalize_text(x) for x in s.split("|") if x.strip()]
        if "\n" in s:
            return [normalize_text(x) for x in s.split("\n") if x.strip()]
        return [s]


def strip_leading_qty(s: str) -> str:
    """
    Remove leading quantity & measurements to expose ingredient name for matching.
    Example: '1 cup evaporated milk' -> 'evaporated milk'
    This is intentionally conservative: we remove common leading patterns.
    """
    if not s:
        return ""
    s = s.lower()
    # common patterns: numbers, fractions, parentheses, measurements at start
    # remove leading parenthetical groups or leading numbers/fractions/measurements
    s = re.sub(
        r"^\s*\(?\d+(?:[\/\u00BC-\u00BE\u2150-\u215E]?\d*)?\)?\s*", "", s
    )  # leading numbers like "1", "1/2"
    s = re.sub(
        r"^\s*\d+(\.\d+)?\s*(cup|cups|tbsp|tbsp.|tbsps|tsp|tsp.|oz|lb|lbs|g|kg|ml|l)\b",
        "",
        s,
    )
    s = re.sub(r"^\s*(?:one|two|three|four|a|an)\s+", "", s)  # words
    # remove leftover leading measurement words
    s = re.sub(r"^\s*\(?\d+[^a-zA-Z]*\)?\s*", "", s)
    # strip extras
    s = re.sub(r"^[\-\–\—\s]+", "", s)
    return s.strip()


# Use st.cache_data for availability checks.
# Cache key will be the ingredients string and a tuple of pantry products (for hashing).
@st.cache_data
def cached_check_availability(
    recipe_ingredients: str, pantry_products_tuple: Tuple[str, ...]
) -> Tuple[float, List[str]]:
    """Return (match_percent, missing_items_list) using strict whole-word matching."""
    ingredients = parse_ingredients(recipe_ingredients)
    if not ingredients:
        return 0.0, []

    total = len(ingredients)
    available_count = 0
    missing_items = []

    # convert pantry regex list from pantry_products_tuple each call for safety
    regexes = [
        re.compile(rf"\b{re.escape(p)}\b", flags=re.IGNORECASE)
        for p in pantry_products_tuple
    ]

    for item in ingredients:
        item_norm = normalize_text(item).lower()
        # strip leading qty to focus on name
        name_candidate = strip_leading_qty(item_norm)
        # fallback to full item if strip produced emptiness
        text_to_search = name_candidate or item_norm

        matched = False
        for rx in regexes:
            if rx.search(text_to_search):
                matched = True
                break

        if matched:
            available_count += 1
        else:
            # record a cleaned short name as missing
            # take last 3 words of the name candidate to make missing hint concise
            words = text_to_search.split()
            short = " ".join(words[-3:]) if len(words) > 3 else " ".join(words)
            missing_items.append(short)

    match_percentage = (available_count / total) * 100 if total > 0 else 0.0
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
total_recipes = len(recipes)

# Convert pantry_products to tuple for caching
pantry_key = tuple(pantry_products)

for idx, (_, row) in enumerate(recipes.iterrows()):
    # Update progress (user requested not to throttle updates)
    progress = (idx + 1) / total_recipes
    progress_bar.progress(progress)
    status_text.text(f"Processing recipe {idx + 1} of {total_recipes}...")

    # Safely get ingredients string
    ingredients_raw = normalize_text(row.get("Ingredients") or "")
    match_percent, missing = cached_check_availability(ingredients_raw, pantry_key)

    if match_percent >= min_match:
        instr = normalize_text(row.get("Instructions") or "")
        # Shorten instructions safely
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

# Clear progress indicators
progress_bar.empty()
status_text.empty()

# Sort and limit results
results_df = pd.DataFrame(results)
if not results_df.empty:
    results_df = results_df.sort_values(by="Match %", ascending=False).head(
        int(max_recipes)
    )
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
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Match:** {row['Match %']}%")
                st.markdown(f"**Missing:** {row['Missing']}")

            # Ingredients: parse and display safely
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
        f"No recipes found with at least {min_match}% match. Try lowering the minimum match percentage."
    )
