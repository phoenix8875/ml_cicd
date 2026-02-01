import streamlit as st
import pickle
import pandas as pd
import requests
import re
from sklearn.metrics.pairwise import cosine_similarity

import os
from dotenv import load_dotenv

# This looks for the .env file when running locally
load_dotenv()

# This grabs the key from the OS (provided by .env or Jenkins/Docker)
API_KEY = os.getenv('OMDB_API_KEY')

if not API_KEY:
    st.error("Missing API Key! Please check your environment variables.")

# Custom CSS for the "Netflix-Style" Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stHeading h1 { color: #E50914; text-align: center; font-family: 'Arial Black', sans-serif; }
    .movie-card { text-align: center; background-color: #1a1c23; border-radius: 10px; padding: 10px; }
    .stImage > img { 
        border-radius: 10px; 
        transition: transform 0.3s; 
        height: 350px; 
        object-fit: cover; 
        width: 100%;
    }
    .stImage > img:hover { transform: scale(1.05); border: 2px solid #E50914; }
    .movie-title { font-size: 14px; font-weight: bold; margin-top: 10px; height: 40px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING ---
@st.cache_resource
def load_data():
    # Ensure these files are in your /model directory
    movies = pickle.load(open('model/movies_list.pkl', 'rb'))
    vector_matrix = pickle.load(open('model/vector_matrix.pkl', 'rb'))
    return movies, vector_matrix

try:
    movies, vector_matrix = load_data()
except FileNotFoundError:
    st.error("Model files not found! Please run your Jupyter Notebook first.")
    st.stop()

# --- 3. THE POSTER FETCHING ENGINE ---
def get_movie_poster(movie_title):
    """Cleans MovieLens titles and fetches posters from OMDb"""
    try:
        # Step A: Remove Year in parentheses: "Toy Story (1995)" -> "Toy Story"
        clean_title = re.sub(r'\s\(\d{4}\)', '', movie_title).strip()
        
        # Step B: Handle "Title, The" format: "Avengers, The" -> "The Avengers"
        if ", The" in clean_title:
            clean_title = "The " + clean_title.replace(", The", "")
        
        # Step C: API Call
        url = f"http://www.omdbapi.com/?t={clean_title}&apikey={API_KEY}"
        response = requests.get(url, timeout=5).json()
        
        if response.get('Response') == 'True' and response.get('Poster') != 'N/A':
            return response['Poster']
    except Exception as e:
        print(f"Error fetching {movie_title}: {e}")
    
    # Fallback to a placeholder if API fails or Key is inactive
    return "https://via.placeholder.com/500x750?text=Poster+Unavailable"

# --- 4. RECOMMENDATION LOGIC ---
def recommend(movie_title):
    try:
        # Find index of movie
        idx = movies[movies['title'] == movie_title].index[0]
        
        # Calculate Cosine Similarity
        distances = cosine_similarity(vector_matrix[idx], vector_matrix).flatten()
        
        # Get top 10 indices (skipping the 0th index which is the movie itself)
        indices = distances.argsort()[-11:-1][::-1]
        
        results = []
        for i in indices:
            title = movies.iloc[i].title
            results.append({
                "title": title,
                "poster": get_movie_poster(title)
            })
        return results
    except Exception as e:
        st.error(f"Recommendation Error: {e}")
        return []

# --- 5. USER INTERFACE ---
st.title("🎬 MOVIE MATCHER AI")

selected_movie = st.selectbox(
    "Select a movie you enjoyed:",
    movies['title'].values,
    index=None,
    placeholder="Type to search among 32M movies..."
)

if st.button('Recommend 10 Similar Movies'):
    if selected_movie:
        with st.spinner('Syncing with OMDb and calculating similarity...'):
            recs = recommend(selected_movie)
            
            if recs:
                st.write("---")
                st.subheader(f"Because you liked: {selected_movie}")
                
                # Grid Layout (2 Rows of 5)
                for row_idx in range(2):
                    cols = st.columns(5)
                    for col_idx in range(5):
                        movie_num = row_idx * 5 + col_idx
                        with cols[col_idx]:
                            st.image(recs[movie_num]['poster'])
                            st.markdown(f"<p class='movie-title'>{recs[movie_num]['title']}</p>", unsafe_allow_html=True)
            else:
                st.warning("We couldn't find matches for this specific title.")
    else:
        st.info("Please select a movie from the dropdown menu above.")

# --- 6. FOOTER ---
st.markdown("---")
st.caption("Developed by raazz | Data Source: MovieLens & OMDb API")