
import re


PROTEIN_KEYWORDS = {
    "chicken": ["chicken"],
    "beef": ["beef", "meat", "steak"],
    "eggs": ["egg", "eggs"],
    "legumes": ["beans", "lentils", "peas", "legumes"],
    "grains": ["rice", "grains"],
    "none": ["no protein"],
}


def contains_phrase(message, phrase):
    return bool(
        re.search(
            rf"(?<!\w){re.escape(phrase)}(?!\w)",
            message,
            re.IGNORECASE,
        )
    )


def extract_budget(message):
    patterns = [
        r"(?:under|below|less than|maximum|max)\s*(\d+(?:\.\d+)?)",
        r"(?:budget|have|got|spend|spending)\s*(?:of|is|around|about)?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:birr|etb)",
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def extract_preference(message, positive_words, negative_words):
    # Handle non-vegetarian before checking vegetarian.
    if "vegetarian" in positive_words:
        if contains_phrase(message, "non-vegetarian") or contains_phrase(
            message, "non vegetarian"
        ):
            return False

    for word in sorted(positive_words, key=len, reverse=True):
        pattern = (
            rf"\b(?:no|not|without|don't want|do not want|avoid|less)\b"
            rf"(?:\s+\w+){{0,3}}\s+{re.escape(word)}\b"
        )

        if re.search(pattern, message, re.IGNORECASE):
            return False

    for word in positive_words:
        if contains_phrase(message, word):
            return True

    for word in negative_words:
        if contains_phrase(message, word):
            return False

    return None


def extract_excluded_proteins(message):
    excluded = []

    exclusion_pattern = (
        r"\b(?:anything except|anything but|except|avoid|"
        r"without|no|not|don't want|do not want)\s+"
    )

    for protein, keywords in PROTEIN_KEYWORDS.items():
        if protein == "none":
            continue

        for keyword in keywords:
            pattern = exclusion_pattern + re.escape(keyword) + r"\b"

            if re.search(pattern, message, re.IGNORECASE):
                excluded.append(protein)
                break

    return excluded


def extract_protein(message, excluded_proteins=None):
    excluded_proteins = excluded_proteins or []

    for protein, keywords in PROTEIN_KEYWORDS.items():
        if protein in excluded_proteins:
            continue

        for keyword in keywords:
            if contains_phrase(message, keyword):
                return protein

    return None


def extract_appetite(message):
    high_appetite = [
        "starving",
        "very hungry",
        "really hungry",
        "extremely hungry",
        "super hungry",
    ]

    low_appetite = [
        "not very hungry",
        "not hungry",
        "slightly hungry",
        "a little hungry",
    ]

    if any(word in message for word in high_appetite):
        return "high"

    if any(word in message for word in low_appetite):
        return "low"

    if "hungry" in message:
        return "medium"

    return None


def extract_mood(message):
    mood_keywords = {
        "happy": ["happy", "celebrating", "excited"],
        "sad": ["sad", "down", "feeling low"],
        "stressed": ["stressed", "stressful", "overwhelmed"],
        "tired": ["tired", "exhausted", "sleepy"],
        "relaxed": ["relaxed", "calm", "chilling"],
    }

    for mood, keywords in mood_keywords.items():
        for keyword in keywords:
            if not contains_phrase(message, keyword):
                continue

            negation = (
                rf"\b(?:not|never|don't feel|do not feel|"
                rf"am not|isn't|aren't)\s+"
                rf"(?:\w+\s+){{0,2}}{re.escape(keyword)}\b"
            )

            if re.search(negation, message, re.IGNORECASE):
                continue

            return mood

    return None


def extract_meal_type(message):
    meal_keywords = {
        "breakfast": ["breakfast", "morning meal"],
        "lunch": ["lunch"],
        "dinner": ["dinner", "supper"],
        "snack": ["snack", "something small", "quick bite"],
    }

    for meal_type, keywords in meal_keywords.items():
        if any(contains_phrase(message, word) for word in keywords):
            return meal_type

    return None


def extract_price_sensitivity(message):
    affordable_words = [
        "cheap",
        "affordable",
        "budget-friendly",
        "inexpensive",
        "save money",
        "low cost",
        "don't have much money",
        "do not have much money",
        "not much money",
        "tight budget",
        "short on money",
    ]

    premium_words = [
        "expensive",
        "premium",
        "luxury",
        "special treat",
        "splurge",
    ]

    if any(word in message for word in affordable_words):
        return "budget"

    if any(word in message for word in premium_words):
        return "premium"

    return None


def understand_request(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Please describe what you want to eat.")

    text = message.lower()

    excluded_proteins = extract_excluded_proteins(text)

    return {
        "budget": extract_budget(text),

        "spicy": extract_preference(
            text,
            ["spicy", "hot food", "chili", "chilli"],
            ["mild", "not spicy"],
        ),

        "vegetarian": extract_preference(
            text,
            ["vegetarian", "vegan", "plant-based"],
            ["non-vegetarian"],
        ),

        "light_meal": extract_preference(
            text,
            ["light meal", "light food", "something light"],
            ["heavy meal", "heavy food"],
        ),

        "protein": extract_protein(text, excluded_proteins),

        "excluded_proteins": excluded_proteins,

        "appetite": extract_appetite(text),

        "mood": extract_mood(text),

        "meal_type": extract_meal_type(text),

        "price_sensitivity": extract_price_sensitivity(text),
    }
