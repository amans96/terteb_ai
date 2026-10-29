
from pathlib import Path

import pandas as pd


# Find the project root based on this file's location.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MENU_FILE = PROJECT_ROOT / "data" / "menu.csv"


def load_menu():
    """Load the restaurant menu from the CSV file."""
    if not MENU_FILE.exists():
        raise FileNotFoundError(
            f"Menu file not found: {MENU_FILE}"
        )

    menu = pd.read_csv(MENU_FILE)

    required_columns = {
        "item_id",
        "name",
        "category",
        "price",
        "spicy",
        "vegetarian",
        "protein",
        "light_meal",
        "available",
    }

    missing_columns = required_columns - set(menu.columns)

    if missing_columns:
        raise ValueError(
            f"Menu CSV is missing columns: {sorted(missing_columns)}"
        )

    # Convert CSV text values into consistent Python data types.
    for column in ["spicy", "vegetarian", "light_meal", "available"]:
        if menu[column].dtype == object:
            menu[column] = (
                menu[column]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({"true": True, "false": False})
            )

    menu["price"] = pd.to_numeric(menu["price"], errors="raise")

    if menu[["spicy", "vegetarian", "light_meal", "available"]].isna().any().any():
        raise ValueError(
            "Some boolean columns contain invalid values. "
            "Use true or false in menu.csv."
        )

    return menu
