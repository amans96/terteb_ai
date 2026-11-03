
from src.intent_parser import understand_request


messages = [
    # Basic preference tests
    "I have 350 birr and want chicken, not spicy.",
    "Give me something vegetarian under 250 ETB.",
    "I want something light with beef.",
    "I want spicy food with eggs.",

    # Context tests
    "I'm starving and feeling tired. I want something affordable.",
    "I'm a little hungry and want a snack.",
    "I'm celebrating and want something premium for dinner.",
    "I'm stressed and need something light.",

    # Language edge-case tests
    "I don't want spicy food.",
    "I prefer non-vegetarian food.",
    "I'm not tired.",
    "I don't have much money.",
    "Anything except chicken.",
    "I'm not hungry.",
    "I want something mild with beef.",
]


for message in messages:
    print("\nCustomer:", message)
    print("Understood:", understand_request(message))
