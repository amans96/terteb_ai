
def recommend_food(
    menu,
    budget=None,
    spicy=None,
    vegetarian=None,
    light_meal=None,
    protein=None,
    excluded_proteins=None,
    appetite=None,
    mood=None,
    meal_type=None,
    price_sensitivity=None,
    limit=5,
):
    """
    Rank available menu items using customer preferences and context.

    Hard constraints:
    - Food must be available.
    - Food must fit the budget, when a budget is provided.
    - Explicitly excluded proteins are never recommended.

    Soft preferences:
    - Spicy, vegetarian, light meal, protein, appetite.
    - Price sensitivity affects ranking.
    """

    if budget is not None and budget < 0:
        raise ValueError("Budget cannot be negative.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    excluded_proteins = {
        item.strip().lower()
        for item in (excluded_proteins or [])
    }

    # Start with available food.
    candidates = menu[menu["available"] == True].copy()

    # Apply budget only when the customer provides one.
    if budget is not None:
        candidates = candidates[candidates["price"] <= budget]

    # Excluded proteins are hard constraints.
    if excluded_proteins and "protein" in candidates.columns:
        candidates = candidates[
            ~candidates["protein"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(excluded_proteins)
        ]

    if candidates.empty:
        candidates["score"] = 0
        return candidates

    candidates["score"] = 0

    # Score explicit food preferences.
    preferences = {
        "spicy": spicy,
        "vegetarian": vegetarian,
        "light_meal": light_meal,
    }

    for feature, preference in preferences.items():
        if preference is not None and feature in candidates.columns:
            matches = candidates[feature] == preference
            candidates["score"] += matches.map({
                True: 2,
                False: -1,
            })

    # Score preferred protein.
    if protein is not None and "protein" in candidates.columns:
        matches = (
            candidates["protein"]
            .astype(str)
            .str.strip()
            .str.lower()
            == protein.strip().lower()
        )

        candidates["score"] += matches.map({
            True: 2,
            False: -1,
        })

    # Appetite provides a soft signal about meal size.
    if appetite == "high" and "light_meal" in candidates.columns:
        candidates["score"] += (
            candidates["light_meal"] == False
        ).map({True: 2, False: 0})

    elif appetite == "low" and "light_meal" in candidates.columns:
        candidates["score"] += (
            candidates["light_meal"] == True
        ).map({True: 2, False: 0})

    # Price sensitivity affects ranking, not eligibility.
    if price_sensitivity == "budget":
        candidates = candidates.sort_values(
            by=["score", "price"],
            ascending=[False, True],
        )

    else:
        candidates = candidates.sort_values(
            by=["score", "price"],
            ascending=[False, True],
        )

    return candidates.head(limit)
