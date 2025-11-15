"""
Recipe Dataset Cleaning

This script cleans and processes the recipe dataset, adding useful metadata columns.
"""

from pathlib import Path
import pandas as pd


def extract_keywords(title):
    """Extract main keywords from recipe title."""
    exclude = {"with", "and", "the", "for", "from", "or"}
    words = str(title).lower().split()
    keywords = [w for w in words if w not in exclude and len(w) > 3]
    return keywords[:3]


def is_vegetarian(ingredients_list):
    """Check if recipe is vegetarian based on ingredients."""
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

    ingredients_text = " ".join([str(ing).lower() for ing in ingredients_list])
    return not any(keyword in ingredients_text for keyword in non_veg_keywords)


def main():
    """Main function to clean recipe dataset."""
    base_dir = Path(__file__).resolve().parent / "data"

    # Load the recipe dataset
    print("Loading recipe dataset...")
    df = pd.read_csv(base_dir / "Recipe_Dataset.csv")
    print(f"Dataset shape: {df.shape}")

    # Add ingredient count
    print("\nAdding ingredient count...")
    df["ingredient_count"] = df["Ingredients"].apply(len)
    print(f"Average ingredients per recipe: {df['ingredient_count'].mean():.1f}")

    # Count instruction steps
    print("\nCounting instruction steps...")
    df["instruction_steps"] = df["Instructions"].apply(
        lambda x: len([s for s in str(x).split(".") if s.strip()])
    )
    print(f"Average steps per recipe: {df['instruction_steps'].mean():.1f}")

    # Extract keywords from titles
    print("\nExtracting keywords...")
    df["keywords"] = df["Title"].apply(extract_keywords)

    # Identify vegetarian recipes
    print("\nIdentifying vegetarian recipes...")
    df["vegetarian"] = df["Ingredients"].apply(is_vegetarian)

    # Check for duplicates
    print("\nChecking for duplicates...")
    duplicates = df.duplicated(subset=["Title"], keep="first")
    print(f"Duplicate recipes found: {duplicates.sum()}")

    if duplicates.sum() > 0:
        print("Removing duplicates...")
        df = df.drop_duplicates(subset=["Title"], keep="first")
        print(f"Shape after removing duplicates: {df.shape}")

    # Reset index
    df = df.reset_index(drop=True)
    print("Index reset complete.")

    # Save cleaned dataset
    print("\nSaving cleaned dataset...")
    output_path = base_dir / "cleaned_recipes.csv"
    df.to_csv(output_path, index=False)
    print(f"Data saved to '{output_path}'")

    # Load pantry data
    print("\nLoading pantry data...")
    df2 = pd.read_excel(base_dir / "pantry_data.xlsx")
    print(f"Pantry data shape: {df2.shape}")

    print("\nCleaning complete!")


if __name__ == "__main__":
    main()
