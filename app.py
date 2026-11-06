
import streamlit as st

from src.data_loader import load_menu
from src.llm_client import understand_food_request
from src.recommender import recommend_food


st.set_page_config(
    page_title="Terteb AI",
    page_icon="🍽️",
    layout="centered",
)


@st.cache_data
def get_menu():
    return load_menu()


st.title("Terteb AI")
st.subheader("Your personal food recommendation assistant")

st.write(
    "Tell me what you're craving, your budget, "
    "and how you're feeling. I'll find suitable dishes."
)

try:
    menu = get_menu()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load menu: {error}")
    st.stop()


message = st.text_area(
    "What would you like to eat?",
    placeholder=(
        "Example: I'm starving, feeling tired, "
        "and have 350 birr. I want chicken, not spicy."
    ),
    height=120,
)

limit = st.selectbox(
    "Number of recommendations",
    [3, 5, 10],
    index=1,
)


if st.button("Find my food", type="primary"):

    if not message.strip():
        st.warning("Tell me what you're looking for first.")

    else:
        try:
            # 1. Let the LLM understand the customer's message.
            intent = understand_food_request(message)

            st.subheader("What I understood")
            st.json(intent)

            # 2. Check whether this request is for food recommendations.
            if intent["intent"] != "recommend_food":
                st.info(
                    "This request is not a food recommendation "
                    "request yet. We'll support other ordering "
                    "actions in a later stage."
                )
                st.stop()

            # 3. Pass the LLM's structured output to Python.
            recommendations = recommend_food(
                menu=menu,
                budget=intent["budget"],
                spicy=intent["spicy"],
                vegetarian=intent["vegetarian"],
                light_meal=intent["light_meal"],
                protein=intent["protein"],
                excluded_proteins=intent["excluded_proteins"],
                appetite=intent["appetite"],
                mood=intent["mood"],
                meal_type=intent["meal_type"],
                price_sensitivity=intent["price_sensitivity"],
                limit=limit,
            )

            # 4. Display recommendations from the real menu.
            st.subheader("Your food recommendations")

            if recommendations.empty:
                st.warning(
                    "I couldn't find suitable available dishes. "
                    "Try changing your preferences or budget."
                )

            else:
                for _, dish in recommendations.iterrows():
                    with st.container(border=True):
                        st.subheader(dish["name"])
                        st.write(f"**Price:** {dish['price']:,.0f} ETB")
                        st.write(f"**Category:** {dish['category']}")
                        st.write(f"**Score:** {dish['score']}")

            st.caption(
                "Terteb uses an LLM to understand requests "
                "and a Python recommendation engine to rank "
                "real menu items."
            )

        except (ValueError, KeyError) as error:
            st.error(f"Something went wrong: {error}")

        except Exception as error:
            st.error(f"Could not process your request: {error}")
