
import streamlit as st
import pandas as pd
import numpy as np
import requests
from streamlit_searchbox import st_searchbox

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""

<style>

/* ---------- Background ---------- */

.stApp{
    background:#141414;
}

/* ---------- Hide Streamlit ---------- */

[data-testid="stSidebar"]{
    display:none;
}

[data-testid="collapsedControl"]{
    display:none;
}

[data-testid="stHeader"]{
    display:none;
}

/* ---------- Title ---------- */

h1{
    color:#E50914;
    text-align:center;
    font-size:3rem;
}

/* ---------- Images ---------- */

img{
    border-radius:12px;
    transition:0.3s;
}
a:hover{
    color:#E50914 !important;
}

img:hover{
    transform:scale(1.05);
}

/* ---------- Buttons ---------- */

.stButton>button{

    width:100%;

    border-radius:8px;

    background:#E50914;

    color:white;

    border:none;

    font-weight:bold;
}

/* ---------- Search ---------- */

div[data-testid="stSelectbox"]{

    margin-top:15px;

}

</style>
""", unsafe_allow_html=True)




# ==================================================
# LOAD DATA
# ==================================================

movies = pd.read_csv("data/movies.csv")

similarity = np.load("data/similarity.npy")

# ==================================================
# TMDB API
# ==================================================

API_KEY = ""


# ==================================================
# FETCH COMPLETE MOVIE DETAILS
# ==================================================

def fetch_movie_details(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={API_KEY}"
    )

    try:

        response = requests.get(url)

        data = response.json()

        poster = None

        if data.get("poster_path"):

            poster = (
                "https://image.tmdb.org/t/p/w500"
                + data["poster_path"]
            )

        return {

            "poster": poster,

            "rating": data.get(
                "vote_average",
                "N/A"
            ),

            "runtime": data.get(
                "runtime",
                "N/A"
            ),

            "overview": data.get(
                "overview",
                "No overview available."
            ),

            "year": str(
                data.get(
                    "release_date",
                    ""
                )
            )[:4],

            "genres": ", ".join(

                genre["name"]

                for genre in data.get(
                    "genres",
                    []
                )

            ),

            "imdb_id": data.get(
                "imdb_id",
                ""
            )

        }

    except:

        return {

            "poster": None,

            "rating": "N/A",

            "runtime": "N/A",

            "overview": "Unavailable",

            "year": "N/A",

            "genres": "N/A",

            "imdb_id": ""

        }

# ==================================================
# RECOMMEND MOVIES
# ==================================================

def recommend(movie_title):

    movie_index = movies[
        movies["title"] == movie_title
    ].index[0]

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:11]

    # Selected movie

    selected_movie_id = movies.iloc[
        movie_index
    ].movie_id

    selected_movie = fetch_movie_details(
        selected_movie_id
    )

    selected_movie["title"] = movie_title

    recommendations = []

    for movie in movie_list:

        idx = movie[0]

        movie_id = movies.iloc[idx].movie_id

        details = fetch_movie_details(
            movie_id
        )

        details["title"] = movies.iloc[idx].title

        recommendations.append(
            details
        )

    return selected_movie, recommendations

# ==================================================
# SEARCH SUGGESTIONS
# ==================================================

def search_movies(searchterm: str):

    if not searchterm:
        return []

    return [
        movie
        for movie in movies["title"].tolist()
        if searchterm.lower() in movie.lower()
    ][:8]


# ==================================================
# APP TITLE
# ==================================================

st.markdown(
    """
    <h1>
        🎬 NETFLIX MOVIE RECOMMENDER
    </h1>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SEARCH BAR
# ==================================================

left, center, right = st.columns([1,3,1])

with center:

    selected_movie = st_searchbox(
        search_movies,
        placeholder="🎬 Search any movie...",
        key="movie_search"
    )


    
# ==================================================
# FETCH RECOMMENDATIONS
# ==================================================

if selected_movie:

    with st.spinner("🎬 Finding similar movies..."):
        selected_movie_data, recommendations = recommend(selected_movie)

    st.markdown("---")
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ==================================================
    # HERO SECTION
    # ==================================================

    left, right = st.columns([1, 2])

    with left:

        if selected_movie_data["poster"]:

            st.image(
                selected_movie_data["poster"],
                use_container_width=320
            )

    with right:

        st.markdown(
            f"""
            <h1 style="color:white;margin-bottom:0px;">
            {selected_movie_data["title"]}
            </h1>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <p style="color:#BBBBBB;font-size:18px;">

            ⭐ {selected_movie_data["rating"]}

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🎭 {selected_movie_data["genres"]}

            &nbsp;&nbsp;|&nbsp;&nbsp;

            🕒 {selected_movie_data["runtime"]} min

            &nbsp;&nbsp;|&nbsp;&nbsp;

            📅 {selected_movie_data["year"]}

            </p>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                color:#DDDDDD;
                font-size:18px;
                line-height:1.8;
                text-align:justify;
            ">
            {selected_movie_data["overview"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.markdown(
    f"""
    <a href="https://www.imdb.com/title/{selected_movie_data['imdb_id']}"
       target="_blank"
       style="
           display:inline-block;
           padding:12px 22px;
           background:#202020;
           color:white;
           border:1px solid #E50914;
           border-radius:10px;
           text-decoration:none;
           font-weight:bold;
       ">
       🎬 View on IMDb
    </a>
    """,
    unsafe_allow_html=True
)
        


    st.write("")
    st.write("")

    # ==================================================
    # RECOMMENDATION TITLE
    # ==================================================

    st.markdown(
        f"""
        <h2 style="color:white;">
        Because you liked
        <span style="color:#E50914;">
        {selected_movie}
        </span>
        </h2>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # FIRST ROW
    # ==================================================

    cols = st.columns(5)

    for i in range(5):

        movie = recommendations[i]

        with cols[i]:

            if movie["poster"]:

                st.image(
                    movie["poster"],
                    use_container_width=True
                )

            st.markdown(
                f"""
                <h4 style="
                    color:white;
                    text-align:center;
                    min-height:60px;
                ">
                {movie["title"]}
                </h4>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <p style="
                    text-align:center;
                    color:#BBBBBB;
                ">
                ⭐ {movie["rating"]}
                </p>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
    f"""
    <div style="text-align:center;">
        <a href="https://www.imdb.com/title/{movie['imdb_id']}"
           target="_blank"
           style="
               display:inline-block;
               padding:8px 18px;
               background:#202020;
               color:white;
               border:1px solid #555;
               border-radius:8px;
               text-decoration:none;
               font-weight:bold;
           ">
           IMDb
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


    st.write("")
    st.write("")

    # ==================================================
    # SECOND ROW
    # ==================================================

    cols = st.columns(5)

    for i in range(5, 10):

        movie = recommendations[i]

        with cols[i - 5]:

            if movie["poster"]:

                st.image(
                    movie["poster"],
                    use_container_width=True
                )

            st.markdown(
                f"""
                <h4 style="
                    color:white;
                    text-align:center;
                    min-height:60px;
                ">
                {movie["title"]}
                </h4>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <p style="
                    text-align:center;
                    color:#BBBBBB;
                ">
                ⭐ {movie["rating"]}
                </p>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
    f"""
    <div style="text-align:center;">
        <a href="https://www.imdb.com/title/{movie['imdb_id']}"
           target="_blank"
           style="
               display:inline-block;
               padding:8px 18px;
               background:#202020;
               color:white;
               border:1px solid #555;
               border-radius:8px;
               text-decoration:none;
               font-weight:bold;
           ">
           IMDb
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

            
