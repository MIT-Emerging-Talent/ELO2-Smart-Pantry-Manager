# spell-checker: disable
"""
Clean recipe CSV and create SQLite DB with diet type.
"""

import re
import sqlite3

import pandas as pd

# Load CSV
df = pd.read_csv("smart_pantry_manager/data/Recipe_Dataset.csv")

# Forbidden (haram) ingredients
haram_keywords = [
    "pork",
    "ham",
    "bacon",
    "prosciutto",
    "pancetta",
    "sausage",
    "wine",
    "beer",
    "bourbon",
    "rum",
    "whisky",
    "vodka",
    "tequila",
    "cognac",
    "brandy",
    "liqueur",
    "alcohol",
    "champagne",
    "sake",
    "sherry",
    "gin",
]

# Meat ingredients
meat_keywords = [
    "chicken",
    "beef",
    "lamb",
    "turkey",
    "fish",
    "shrimp",
    "salmon",
    "tuna",
    "meat",
    "steak",
    "duck",
    "anchovy",
    "crab",
    "lobster",
    "clam",
    "oyster",
    "scallop",
    "mussel",
    "squid",
    "sausage",
]

# Animal products (vegetarian)
animal_product_keywords = [
    "egg",
    "milk",
    "cheese",
    "butter",
    "cream",
    "yogurt",
    "ghee",
    "honey",
    "mayonnaise",
    "whey",
    "casein",
    "gelatin",
]


# Check haram
def contains_haram(ingredient_text):
    if pd.isna(ingredient_text):
        return False
    text = ingredient_text.lower()
    for kw in haram_keywords:
        if re.search(rf"\b{kw}\b", text):
            return True
    return False


# Classify diet type
def classify_diet_type(ingredient_text):
    if pd.isna(ingredient_text):
        return "Unknown"
    text = ingredient_text.lower()
    for kw in meat_keywords:
        if re.search(rf"\b{kw}\b", text):
            return "Non-Vegetarian"
    for kw in animal_product_keywords:
        if re.search(rf"\b{kw}\b", text):
            return "Vegetarian"
    return "Vegan"


# Filter haram
df["contains_haram"] = df["Ingredients"].apply(contains_haram)
df_clean = df[~df["contains_haram"]].copy()
df_clean["Diet_Type"] = df_clean["Ingredients"].apply(classify_diet_type)
df_clean.drop("contains_haram", axis=1, inplace=True)

# SQLite DB
conn = sqlite3.connect("smart_pantry_manager/data/cleaned_data.sqlite")

# Tables for each diet type
for diet in ["Vegan", "Vegetarian", "Non-Vegetarian"]:
    diet_df = df_clean[df_clean["Diet_Type"] == diet].copy()
    diet_df.to_sql(
        diet.lower().replace("-", "_") + "_recipes",
        conn,
        if_exists="replace",
        index=False,
    )

# Combined table
df_clean.to_sql("all_recipes", conn, if_exists="replace", index=False)

conn.close()
print("✅ SQLite DB created with all_recipes and diet tables.")
