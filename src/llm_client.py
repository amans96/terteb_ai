
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("FREEMODEL_API_KEY")
BASE_URL = os.getenv(
    "FREEMODEL_BASE_URL",
    "https://api.groq.com/openai/v1"
)
MODEL_NAME = os.getenv(
    "FREEMODEL_MODEL",
    "openai/gpt-oss-20b"
)

if not API_KEY:
    raise RuntimeError(
        "API key is missing. Check your .env file."
    )

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=60.0,
    max_retries=2,
)


FOOD_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "recommend_food",
                "ask_question",
                "modify_order",
                "place_order",
                "other"
            ]
        },
        "budget": {
            "type": ["number", "null"]
        },
        "spicy": {
            "type": ["boolean", "null"]
        },
        "vegetarian": {
            "type": ["boolean", "null"]
        },
        "light_meal": {
            "type": ["boolean", "null"]
        },
        "protein": {
            "type": ["string", "null"],
            "enum": [
                "chicken",
                "beef",
                "eggs",
                "legumes",
                "grains",
                "none",
                None
            ]
        },
        "excluded_proteins": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [
                    "chicken",
                    "beef",
                    "eggs",
                    "legumes",
                    "grains"
                ]
            }
        },
        "appetite": {
            "type": ["string", "null"],
            "enum": ["high", "medium", "low", None]
        },
        "mood": {
            "type": ["string", "null"],
            "enum": [
                "happy",
                "sad",
                "stressed",
                "tired",
                "relaxed",
                None
            ]
        },
        "meal_type": {
            "type": ["string", "null"],
            "enum": [
                "breakfast",
                "lunch",
                "dinner",
                "snack",
                None
            ]
        },
        "price_sensitivity": {
            "type": ["string", "null"],
            "enum": ["budget", "premium", None]
        },
        "satiety": {
            "type": ["string", "null"],
            "enum": ["high", "medium", "low", None]
        },
        "dietary_restrictions": {
            "type": "array",
            "items": {"type": "string"}
        },
        "allergies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "intent",
        "budget",
        "spicy",
        "vegetarian",
        "light_meal",
        "protein",
        "excluded_proteins",
        "appetite",
        "mood",
        "meal_type",
        "price_sensitivity",
        "satiety",
        "dietary_restrictions",
        "allergies",
        "missing_information"
    ],
    "additionalProperties": False
}


SYSTEM_PROMPT = """
You are the food request understanding engine for Terteb,
an Ethiopian restaurant ordering assistant.

Your job is to understand what a customer wants and extract
their preferences into structured data.

Rules:

1. Extract only information supported by the customer's message.
2. Do not invent budgets, allergies, dietary restrictions,
   ingredients, or preferences.
3. Use null when a value is unknown or not mentioned.
4. A customer asking for filling or hearty food has high satiety.
5. Infer mood conservatively. Do not diagnose emotions.
6. A request to recommend food is recommend_food.
7. A request to change an existing cart is modify_order.
8. A request to submit an order is place_order.
9. Put explicitly mentioned allergies in allergies.
10. Put other explicitly mentioned dietary restrictions
    in dietary_restrictions.
11. Use missing_information for useful details that may need
    clarification, such as allergies when none were mentioned.
12. Never invent restaurant menu items or prices.

The customer may write naturally, informally, or with spelling errors.
Understand the meaning rather than relying on exact keywords.
"""


def ask_llm(message: str) -> str:
    """Send a normal text request to the language model."""

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Message cannot be empty.")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": message}
        ],
    )

    return response.choices[0].message.content or ""


def understand_food_request(message: str) -> dict:
    """Interpret a customer's food request as structured data."""

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Please describe what you want to eat.")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "terteb_food_request",
                "strict": True,
                "schema": FOOD_REQUEST_SCHEMA
            }
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The AI returned an empty response.")

    result = json.loads(content)

    # Basic application-level validation.
    budget = result["budget"]

    if budget is not None and budget < 0:
        raise ValueError("The AI returned an invalid budget.")

    if not isinstance(result["excluded_proteins"], list):
        raise TypeError("Invalid excluded_proteins value.")

    return result
