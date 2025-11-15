# %% [markdown]
# ## Cleaning Recipe Dataset

# %%
import pandas as pd

# %%
# Load the recipe dataset
df = pd.read_csv(
    r"C:\Users\User\Desktop\ELO2-Smart-Pantry-Manager\the_app\data\Recipe_Dataset.csv"
)

# %%
df.head()
df.info()

# %%
# Count ingredients
df["ingredient_count"] = df["Ingredients"].apply(len)

# %%
df["ingredient_count"]

# %%
# Count instruction steps
df["instruction_steps"] = df["Instructions"].apply(
    lambda x: len([s for s in str(x).split(".") if s.strip()])
)


# %%
def extract_keywords(title):
    """Extract main keywords from recipe title"""
    # Common words to exclude
    exclude = {"with", "and", "the", "for", "from", "or"}
    words = str(title).lower().split()
    keywords = [w for w in words if w not in exclude and len(w) > 3]
    return keywords[:3]  # Return top 3 keywords


df["keywords"] = df["Title"].apply(extract_keywords)


# %%
def is_vegetarian(ingredients_list):
    """Check if recipe is vegetarian based on ingredients"""
    # Non-vegetarian keywords
    non_veg_keywords = [
        "chicken",
        "beef",
        "pork",
        "lamb",
        "turkey",
        "duck",
        "veal",
        "fish",
        "salmon",
        "tuna",
        "shrimp",
        "prawn",
        "lobster",
        "crab",
        "anchovy",
        "anchovies",
        "bacon",
        "ham",
        "sausage",
        "chorizo",
        "meat",
        "steak",
        "ribs",
        "wings",
        "drumstick",
        "thigh",
        "cod",
        "halibut",
        "snapper",
        "sardine",
        "clam",
        "oyster",
        "mussels",
        "scallop",
        "octopus",
        "squid",
        "gelatin",
    ]

    # Convert all ingredients to lowercase string
    ingredients_text = " ".join([str(ing).lower() for ing in ingredients_list])
    for keyword in non_veg_keywords:
        if keyword in ingredients_text:
            return False

    return True


# %%
df["vegetarian"] = df["Ingredients"].apply(is_vegetarian)

print("Sample metadata:")
print(df[["Title", "ingredient_count", "instruction_steps", "vegetarian"]].head(5))
print(
    f"\nVegetarian recipes: {df['vegetarian'].sum()} out of {len(df)} "
    f"({df['vegetarian'].sum()/len(df)*100:.1f}%)"
)


# %%
print("\n" + "=" * 50)
print("Checking for duplicates...")
duplicates = df.duplicated(subset=["Title"], keep="first")
print(f"Duplicate recipes found: {duplicates.sum()}")

if duplicates.sum() > 0:
    print("Removing duplicates...")
    df = df.drop_duplicates(subset=["Title"], keep="first")
    print(f"Shape after removing duplicates: {df.shape}")

# Reset index
print("\n" + "=" * 50)
print("Resetting index...")
df = df.reset_index(drop=True)

# %%
print("\n" + "=" * 50)
print("Final summary...")
print(f"\nFinal shape: {df.shape}")
print(f"\nColumn names: {df.columns.tolist()}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print("\nSample statistics:")
print(df[["ingredient_count", "instruction_steps"]].describe())

# Save cleaned data
print("\n" + "=" * 50)
print("Saving cleaned data...")
df.to_csv("cleaned_recipes.csv", index=False)
print("Data saved to 'cleaned_recipes.csv'")

# %%
df.columns

# %%
df.shape

# %%
# Load pantry data
df2 = pd.read_excel(
    r"C:\Users\User\Desktop\ELO2-Smart-Pantry-Manager\the_app\data\pantry_data.xlsx"
)

# %%
df2.head()

# %%
df2.info()

# %%
df2["Product"].value_counts()
