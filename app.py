import requests
import streamlit as st

# ==========================
# CONFIG
# ==========================

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ==========================
# CSS
# ==========================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    max-width:1400px;
}

.card{
    border-radius:15px;
    padding:10px;
    border:1px solid #ddd;
    background:#11111108;
}

.movie-title{
    text-align:center;
    font-weight:600;
    font-size:15px;
    min-height:45px;
}

.small{
    color:gray;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# API HELPERS
# ==========================

def api_get(path, params=None):
    try:
        r = requests.get(
            API + path,
            params=params
        )

        if r.status_code == 200:
            return r.json()

        return None

    except:
        return None


def api_post(path, data=None, params=None):
    try:
        r = requests.post(
            API + path,
            json=data,
            params=params
        )

        if r.status_code == 200:
            return r.json()

        return None

    except:
        return None


# ==========================
# POSTER GRID
# ==========================

def show_movies(movies):

    cols = st.columns(5)

    for i, movie in enumerate(movies):

        with cols[i % 5]:

            if movie["poster_url"]:
                st.image(movie["poster_url"])

            st.markdown(
                f"<div class='movie-title'>{movie['title']}</div>",
                unsafe_allow_html=True
            )

            st.write("⭐", movie["rating"])

            st.caption(movie["release_date"])


# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("🎬 Movie Recommender")

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Search",
        "Recommend"
    ]
)

st.title("🎬 Movie Recommender")
st.divider()

# ==========================
# HOME PAGE
# ==========================

if page == "Home":

    category = st.selectbox(
        "Category",
        [
            "popular",
            "top_rated",
            "upcoming",
            "now_playing",
            "trending"
        ]
    )

    movies = api_get(
        "/home",
        {
            "category": category
        }
    )

    if movies:

        st.subheader(category.replace("_", " ").title())

        show_movies(movies)

    else:

        st.error("Unable to fetch movies.")


# ==========================
# SEARCH PAGE
# ==========================

elif page == "Search":

    keyword = st.text_input(
        "Search Movie"
    )

    if keyword:

        movies = api_get(
            "/search",
            {
                "title": keyword
            }
        )

        if movies:

            st.subheader("Search Results")

            show_movies(movies)

            st.divider()

            selected = st.selectbox(
                "Choose a movie to view details",
                [movie["title"] for movie in movies]
            )

            if st.button("Show Details"):

                details = api_get(
                    "/movie_details",
                    {
                        "title": selected
                    }
                )

                if details:

                    st.subheader(details["title"])

                    st.write("### Overview")

                    st.write(details["overview"])

                    st.write(
                        "**Language:**",
                        details["original_language"]
                    )

                else:

                    st.error("Movie details not found.")

        else:

            st.warning("No movies found.")

# ==========================
# RECOMMEND PAGE
# ==========================

elif page == "Recommend":

    movie = st.text_input(
        "Enter Movie Name"
    )

    number = st.slider(
        "Number of Recommendations",
        5,
        20,
        10
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Get Recommendations"):

            if movie:

                result = api_post(
                    f"/recommend?n={number}",
                    {
                        "title": movie
                    }
                )

                if result and result["recommendations"]:

                    st.subheader("Recommended Movies")

                    show_movies(
                        result["recommendations"]
                    )

                else:

                    st.error("Movie not found.")

            else:

                st.warning("Enter a movie name.")

    with col2:

        if st.button("Movie Details"):

            if movie:

                details = api_get(
                    "/movie_details",
                    {
                        "title": movie
                    }
                )

                if details:

                    st.subheader(details["title"])

                    st.write("### Overview")

                    st.write(details["overview"])

                    st.write(
                        "**Language:**",
                        details["original_language"]
                    )

                else:

                    st.error("Movie not found.")

            else:

                st.warning("Enter a movie name.")