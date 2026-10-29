
import streamlit as st

from src.data_loader import load_menu
from src.recommender import recommend_food


st.set_page_config(
    page_title="Terteb AI Food Recommender",
    page_icon="🍽️",
    layout="centered",
)


@st.cache_data
def get_menu():
    return load_menu()


st.title("Terteb AI Food Recommender")
st.write(
    "Find dishes that match your budget and food preferences."
)

try:
    menu = get_menu()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the menu: {error}")
    st.stop()


st.subheader("Tell us what you want")

budget = st.number_input(
    "Your budget (ETB)",
    min_value=0,
    value=200,
    step=10,
)


def preference_input(label):
    choice = st.selectbox(
        label,
        ["No preference", "Yes", "No"],
    )

    if choice == "No preference":
        return None

    return choice == "Yes"


spicy = preference_input("Do you want spicy food?")
vegetarian = preference_input("Do you want vegetarian food?")
light_meal = preference_input("Do you want a light meal?")

protein_options = {
    "No preference": None,
    "Chicken": "chicken",
    "Beef": "beef",
    "Eggs": "eggs",
    "Legumes": "legumes",
    "Grains": "grains",
    "No protein preference (none)": "none",
}

protein_choice = st.selectbox(
    "Preferred protein",
    list(protein_options.keys()),
)

protein = protein_options[protein_choice]

limit = st.selectbox(
    "Number of recommendations",
    [3, 5, 10],
    index=1,
)


if st.button("Recommend food", type="primary"):
    recommendations = recommend_food(
        menu=menu,
        budget=budget,
        spicy=spicy,
        vegetarian=vegetarian,
        light_meal=light_meal,
        protein=protein,
        limit=limit,
    )

    st.subheader("Your recommendations")

    if recommendations.empty:
        st.warning(
            "No available dishes fit your budget. "
            "Try increasing your budget."
        )
    else:
        for _, dish in recommendations.iterrows():
            with st.container(border=True):
                st.subheader(dish["name"])
                st.write(f"**Price:** {dish['price']:,.0f} ETB")
                st.write(f"**Category:** {dish['category']}")
                st.write(f"**Preference score:** {dish['score']}")

        st.caption(
            "Recommendations use manually defined scoring rules. "
            "The system has not learned from customer behavior yet."
        )
