import pandas as pd
from src.data_loader import load_menu
from src.recommender import recommend_food


# Load our menu.
menu = load_menu()

# Simulate a customer request.
recommendations = recommend_food(
    menu=menu,
    budget=200,
    spicy=True,
    vegetarian=True,
    light_meal=True,
    limit=5,
)

print("\nRecommended food")
print("----------------")

if recommendations.empty:
    print("No available dishes match your budget.")
else:
    print(
        recommendations[
            ["name", "price", "spicy", "vegetarian", "light_meal", "score"]
        ].to_string(index=False)
    )
