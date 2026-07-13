
import streamlit as st
import requests
import json
import os
from collections import defaultdict

st.set_page_config(page_title="OrbitMeals", page_icon="🍽️", layout="wide")

DATA_FILE = "orbitmeals_data.json"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEAL_SLOTS = ["Breakfast", "Lunch", "Dinner"]
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: radial-gradient(ellipse at top, #14172e 0%, #0a0b1e 45%, #050510 100%); }
    #starfield {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
        background-image:
            radial-gradient(2px 2px at 20px 30px, white, transparent),
            radial-gradient(1.5px 1.5px at 90px 150px, white, transparent),
            radial-gradient(2px 2px at 160px 60px, white, transparent),
            radial-gradient(1px 1px at 250px 200px, white, transparent),
            radial-gradient(1.5px 1.5px at 310px 100px, white, transparent),
            radial-gradient(2px 2px at 400px 250px, white, transparent);
        background-repeat: repeat; background-size: 420px 420px;
        opacity: 0.5; animation: twinkle 6s ease-in-out infinite alternate;
    }
    @keyframes twinkle { from { opacity: 0.3; } to { opacity: 0.7; } }
    .glass-card {
        background: rgba(255,255,255,0.06); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 16px 18px;
        margin-bottom: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    }
    .cosmic-title {
        font-weight: 800; font-size: 2.6rem;
        background: linear-gradient(90deg, #8affc1, #6ee7ff, #b487ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        margin-bottom: 0;
    }
    .cosmic-sub { color: rgba(255,255,255,0.65); font-size: 1.05rem; margin-top: 0; margin-bottom: 20px; }
    .day-header {
        font-weight: 700; font-size: 1.05rem; color: #8affc1; margin-bottom: 8px; text-align: center;
    }
    .slot-label {
        font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em;
        color: rgba(255,255,255,0.45); margin-bottom: 2px;
    }
    .meal-chip {
        background: rgba(110,231,255,0.1); border: 1px solid rgba(110,231,255,0.25);
        border-radius: 10px; padding: 6px 10px; font-size: 0.85rem; color: #d6f6ff;
        margin-bottom: 6px; min-height: 30px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #8affc1, #6ee7ff); color: #0a0b1e; border: none;
        border-radius: 12px; padding: 0.5rem 1.2rem; font-weight: 700; transition: transform 0.15s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(110,231,255,0.35); }
    .shopping-item {
        background: rgba(255,255,255,0.04); border-radius: 8px; padding: 8px 12px;
        margin-bottom: 5px; display: flex; justify-content: space-between; color: rgba(255,255,255,0.85);
    }
    </style>
    <div id="starfield"></div>
    """, unsafe_allow_html=True)

load_css()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"plan": {}, "servings": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "meals_data" not in st.session_state:
    st.session_state.meals_data = load_data()
data = st.session_state.meals_data

@st.cache_data(ttl=3600)
def search_meals(query):
    try:
        r = requests.get(f"{BASE_URL}/search.php?s={query}", timeout=10)
        return r.json().get("meals") or []
    except Exception:
        return []

@st.cache_data(ttl=3600)
def get_meal_details(meal_id):
    try:
        r = requests.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=10)
        meals = r.json().get("meals")
        return meals[0] if meals else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_random_meal():
    try:
        r = requests.get(f"{BASE_URL}/random.php", timeout=10)
        meals = r.json().get("meals")
        return meals[0] if meals else None
    except Exception:
        return None

def extract_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ing and ing.strip():
            ingredients.append((ing.strip(), measure.strip() if measure else ""))
    return ingredients

st.markdown('<p class="cosmic-title">🍽️ OrbitMeals</p>', unsafe_allow_html=True)
st.markdown('<p class="cosmic-sub">Plan your week, generate your shopping list, orbit your kitchen with ease.</p>', unsafe_allow_html=True)

tabs = st.tabs(["📅 Weekly Planner", "🔍 Find Recipes", "🛒 Shopping List"])

# ---------------- WEEKLY PLANNER ----------------
with tabs[0]:
    st.markdown("#### This week's plan")
    st.caption("Click a slot to assign a meal, searched from Find Recipes tab.")

    cols = st.columns(7)
    for i, day in enumerate(DAYS):
        with cols[i]:
            st.markdown(f'<div class="day-header">{day}</div>', unsafe_allow_html=True)
            for slot in MEAL_SLOTS:
                key = f"{day}_{slot}"
                meal_info = data["plan"].get(key)
                st.markdown(f'<div class="slot-label">{slot}</div>', unsafe_allow_html=True)
                if meal_info:
                    st.markdown(f'<div class="meal-chip">{meal_info["name"]}</div>', unsafe_allow_html=True)
                    if st.button("✕", key=f"clear_{key}"):
                        del data["plan"][key]
                        save_data(data)
                        st.rerun()
                else:
                    st.markdown('<div class="meal-chip" style="opacity:0.4;">Empty</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Quick assign")
    qa1, qa2, qa3, qa4 = st.columns([1, 1, 2, 1])
    with qa1:
        qa_day = st.selectbox("Day", DAYS, key="qa_day")
    with qa2:
        qa_slot = st.selectbox("Meal", MEAL_SLOTS, key="qa_slot")
    with qa3:
        qa_search = st.text_input("Search recipe to assign", key="qa_search")
    with qa4:
        st.write("")
        st.write("")
        if st.button("🎲 Random"):
            meal = get_random_meal()
            if meal:
                data["plan"][f"{qa_day}_{qa_slot}"] = {"id": meal["idMeal"], "name": meal["strMeal"]}
                save_data(data)
                st.rerun()

    if qa_search.strip():
        results = search_meals(qa_search.strip())
        if results:
            for meal in results[:5]:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(meal["strMeal"])
                with c2:
                    if st.button("Assign", key=f"assign_{meal['idMeal']}_{qa_day}_{qa_slot}"):
                        data["plan"][f"{qa_day}_{qa_slot}"] = {"id": meal["idMeal"], "name": meal["strMeal"]}
                        save_data(data)
                        st.rerun()
        else:
            st.info("No recipes found. Try another search term.")

    if st.button("🗑️ Clear entire week"):
        data["plan"] = {}
        save_data(data)
        st.rerun()

# ---------------- FIND RECIPES ----------------
with tabs[1]:
    st.markdown("#### Browse recipe ideas")
    search_query = st.text_input("Search for a recipe", placeholder="e.g. chicken curry, pasta, salad")
    if search_query.strip():
        with st.spinner("Searching..."):
            results = search_meals(search_query.strip())
        if not results:
            st.info("No recipes found. Try a different search.")
        else:
            cols = st.columns(3)
            for idx, meal in enumerate(results[:12]):
                with cols[idx % 3]:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    if meal.get("strMealThumb"):
                        st.image(meal["strMealThumb"], use_container_width=True)
                    st.markdown(f"**{meal['strMeal']}**")
                    st.caption(f"{meal.get('strCategory','')} · {meal.get('strArea','')}")
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Search above, or use 'Surprise me' for random ideas.")
        if st.button("🎲 Surprise me with a recipe"):
            meal = get_random_meal()
            if meal:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                cols = st.columns([1, 2])
                with cols[0]:
                    if meal.get("strMealThumb"):
                        st.image(meal["strMealThumb"], use_container_width=True)
                with cols[1]:
                    st.markdown(f"**{meal['strMeal']}**")
                    st.caption(f"{meal.get('strCategory','')} · {meal.get('strArea','')}")
                st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SHOPPING LIST ----------------
with tabs[2]:
    st.markdown("#### Auto-generated shopping list")
    st.caption("Based on all meals currently assigned in your weekly plan.")

    if not data["plan"]:
        st.info("No meals planned yet. Add some in the Weekly Planner tab!")
    else:
        with st.spinner("Gathering ingredients..."):
            ingredient_totals = defaultdict(list)
            seen_ids = set()
            for key, meal_info in data["plan"].items():
                if meal_info["id"] in seen_ids:
                    continue
                seen_ids.add(meal_info["id"])
                details = get_meal_details(meal_info["id"])
                if details:
                    for ing, measure in extract_ingredients(details):
                        ingredient_totals[ing].append(measure)

        if not ingredient_totals:
            st.info("Couldn't load ingredient details. Try refreshing.")
        else:
            st.markdown(f"**{len(ingredient_totals)} unique ingredients across {len(seen_ids)} recipes**")
            for ing, measures in sorted(ingredient_totals.items()):
                measure_str = ", ".join(m for m in measures if m) or "as needed"
                st.markdown(f'''<div class="shopping-item">
                    <span>{ing}</span>
                    <span style="color:rgba(255,255,255,0.5);">{measure_str}</span>
                </div>''', unsafe_allow_html=True)

            list_text = "\n".join(f"- {ing} ({', '.join(m for m in measures if m) or 'as needed'})"
                                   for ing, measures in sorted(ingredient_totals.items()))
            st.download_button("📥 Download shopping list (.txt)", list_text, file_name="shopping_list.txt")

st.markdown("---")
st.markdown('<p style="text-align:center; color:rgba(255,255,255,0.4); font-size:0.85rem;">Powered by TheMealDB · Part of the App Universe ✨</p>', unsafe_allow_html=True)
