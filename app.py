
import streamlit as st

from src.data_loader import load_menu
from src.intent_parser import understand_request
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
    placeholder="Example: I'm starving, feeling tired, "
                "and have 350 birr. I want chicken, not spicy.",
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
            intent = understand_request(message)

            st.subheader("What I understood")
            st.json(intent)

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
                "This prototype uses rule-based intent detection "
                "and recommendation scoring. It is not yet a trained ML model."
            )

        except (ValueError, KeyError) as error:
            st.error(f"Something went wrong: {error}")
