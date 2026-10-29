
def recommend_food(
    menu,
    budget,
    spicy=None,
    vegetarian=None,
    light_meal=None,
    protein=None,
    limit=5,
):
    """
    Recommend available food within the customer's budget.

    Preference values:
    - True or False for spicy, vegetarian, and light_meal
    - A protein name such as "chicken" or "beef"
    - None means the customer has no preference for that feature
    """

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    # Hard constraints: unavailable and unaffordable food is excluded.
    candidates = menu[
        (menu["available"] == True)
        & (menu["price"] <= budget)
    ].copy()

    if candidates.empty:
        return candidates.assign(score=pd.Series(dtype="int64"))

    # Start every candidate with a score of zero.
    candidates["score"] = 0

    # Matching preferences add points; mismatches subtract points.
    preferences = {
        "spicy": spicy,
        "vegetarian": vegetarian,
        "light_meal": light_meal,
    }

    for feature, preference in preferences.items():
        if preference is not None:
            matches = candidates[feature] == preference
            candidates["score"] += matches.map(
                {True: 2, False: -1}
            )

    # Protein is a text category, so compare it without case sensitivity.
    if protein is not None:
        matches = (
            candidates["protein"].astype(str).str.lower()
            == protein.strip().lower()
        )
        candidates["score"] += matches.map(
            {True: 2, False: -1}
        )

    # Prefer higher scores; for equal scores, prefer lower prices.
    candidates = candidates.sort_values(
        by=["score", "price"],
        ascending=[False, True],
    )

    return candidates.head(limit)
