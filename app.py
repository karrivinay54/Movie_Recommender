import streamlit as st
import pandas as pd
import numpy as np
import requests

# ==================================================

# PAGE CONFIGURATION

# ==================================================

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ==================================================

# CUSTOM CSS (NETFLIX STYLE)

# ==================================================

st.markdown("""
<style>

[data-testid="stSidebar"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}

[data-testid="stHeader"] {
    display: none;
}

.stApp {
    background-color: #141414;
}

h1 {
    color: #E50914;
    text-align: center;
}

img {
    border-radius: 12px;
    transition: all 0.3s ease;
}

img:hover {
    transform: scale(1.08);
}

</style>
""", unsafe_allow_html=True)

# ==================================================

# LOAD DATA

# ==================================================

movies = pd.read_csv("movies.csv")
similarity = np.load("similarity.npy")

# ==================================================

# TMDB API SETTINGS

# ==================================================

API_KEY = "d1959c4d05f5f26ce11373450987e590"

# ==================================================

# FETCH POSTER

# ==================================================

def fetch_poster(movie_id):

    try:

        url = (
            f"https://api.themoviedb.org/3/movie/"
            f"{movie_id}?api_key={API_KEY}"
        )

        data = requests.get(url).json()

        poster_path = data.get("poster_path")

        if poster_path:

            return (
                "https://image.tmdb.org/t/p/w500/"
                + poster_path
            )

    except:
        pass

    return None
# ==================================================

# RECOMMENDATION FUNCTION

# ==================================================
def recommend(movie):

    movie_index = movies[
        movies["title"] == movie
    ].index[0]

    selected_movie_poster = fetch_poster(
        movies.iloc[movie_index].movie_id
    )

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []
    recommended_posters = []

    for i in movie_list[1:11]:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        recommended_posters.append(
            fetch_poster(movie_id)
        )

    return (
        selected_movie_poster,
        recommended_movies,
        recommended_posters
    )

def get_year(movie_title):

    row = movies[
        movies["title"] == movie_title
    ]

    if len(row) > 0:

        release_date = row.iloc[0].get(
            "release_date",
            ""
        )

        if pd.notna(release_date):

            return str(
                release_date
            )[:4]

    return "N/A"

# ==================================================

# TITLE

# ==================================================

st.markdown(
    "<h1>🎬 NETFLIX MOVIE RECOMMENDER</h1>",
    unsafe_allow_html=True
)

# ==================================================

# SEARCH BOX

# ==================================================

col1, col2, col3 = st.columns([1,3,1])

with col2:

    selected_movie = st.selectbox(
        "🔍 Search Movie",
        movies["title"].tolist(),
        index=None,
        placeholder="Type a movie name..."
    )


# ==================================================
# AUTO RECOMMENDATION
# ==================================================

if selected_movie:

    with st.spinner(
        "🎬 Searching the movie universe..."
    ):

        selected_poster, recommendations, posters = recommend(
            selected_movie
        )

    # Selected Movie Heading

    st.markdown(
        """
        <h3 style='text-align:center;color:#E50914;'>
        Selected Movie
        </h3>
        """,
        unsafe_allow_html=True
    )

    # Movie Title

    st.markdown(
        f"""
        <h2 style='text-align:center;color:white;'>
        {selected_movie}
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Selected Movie Poster

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:

        if selected_poster:

            st.image(
                selected_poster,
                width=220
            )

    # Recommendation Heading

    st.markdown(
        f"""
        <h3 style='color:white'>
        Because you liked
        <span style='color:#E50914'>
        {selected_movie}
        </span>
        </h3>
        """,
        unsafe_allow_html=True
    )

    # First Row

    cols = st.columns(5)

    for i in range(min(5, len(recommendations))):

        with cols[i]:

            if posters[i]:

                st.image(
                    posters[i],
                    use_container_width=True
                )

            st.caption(
                recommendations[i]
            )

    # Second Row

    if len(recommendations) > 5:

        cols = st.columns(5)

        for i in range(
            5,
            min(10, len(recommendations))
        ):

            with cols[i - 5]:

                if posters[i]:

                    st.image(
                        posters[i],
                        use_container_width=True
                    )

                st.caption(
                    recommendations[i]
                )
