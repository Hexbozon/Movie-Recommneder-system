import requests
import streamlit as st

# --------------------------
# Config
# --------------------------
API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# --------------------------
# Helper Functions
# --------------------------

def api_get(path, params=None):
    try:
        response = requests.get(
            f"{API}{path}",
            params=params
        )
        return response.json()
    except:
        return None


def api_post(path, data=None, params=None):
    try:
        response = requests.post(
            f"{API}{path}",
            json=data,
            params=params
        )
        return response.json()
    except:
        return None

# --------------------------
# UI
# --------------------------

st.title("🎬 Movie Recommender")

tab1, tab2, tab3 = st.tabs(
    [
        "Recommend",
        "Popular",
        "Trending"
    ]
)

# ==========================
# Recommend
# ==========================

with tab1:

    movie = st.text_input("Movie Name")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Movie Details"):

            details = api_get(
                "/movie_details",
                {"title": movie}
            )

            if details:
                st.subheader(details["title"])
                st.write(details["overview"])
                st.write("Language :", details["original_language"])

    with col2:

        if st.button("Recommend"):

            rec = api_post(
                "/recommend?n=10",
                {"title": movie}
            )

            if rec:

                st.subheader("Recommendations")

                for m in rec["recommendations"]:
                    st.write("•", m)

# ==========================
# Popular
# ==========================

with tab2:

    if st.button("Load Popular Movies"):

        movies = api_get("/popular_movies")

        if movies:

            for movie in movies:
                st.write(movie["title"])

# ==========================
# Trending
# ==========================

with tab3:

    option = st.selectbox(
        "Time Window",
        ["day", "week"]
    )

    if st.button("Load Trending"):

        movies = api_get(
            "/trending_movies",
            {"time_window": option}
        )

        if movies:

            for movie in movies:
                st.write(movie["title"])