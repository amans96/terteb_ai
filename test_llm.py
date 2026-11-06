
import json

from src.llm_client import understand_food_request


message = """
I've had a terrible day.
I have 250 ETB.
I want something filling, but I don't want spicy food.
I also don't eat chicken.
"""


try:
    result = understand_food_request(message)

    print("\n===== TERTEB STRUCTURED AI RESPONSE =====\n")

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))

    print("\n===== IMPORTANT VALUES =====")
    print("Intent:", result["intent"])
    print("Budget:", result["budget"], "ETB")
    print("Spicy:", result["spicy"])
    print("Mood:", result["mood"])
    print("Satiety:", result["satiety"])
    print("Excluded proteins:", result["excluded_proteins"])

except Exception as error:
    print(
        f"\nAI request failed: "
        f"{type(error).__name__}: {error}"
    )
