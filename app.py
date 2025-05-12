import streamlit as st
import requests
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JIOSAAVN_API_URL = "https://saavn.dev/api"  # Free unofficial API

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Mood-Based Music App", layout="centered")
st.title("🎧 Mood-Based Music Recommender")

# Session state
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "song_list" not in st.session_state:
    st.session_state.song_list = []

# Mood input
mood_input = st.text_input("How are you feeling today?", placeholder="e.g. Happy, Sad, Energetic")

def get_mood_category(text):
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Classify the user's mood into one of: Happy, Sad, Energetic, Romantic, Calm, Angry"},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=20
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error("Failed to connect to Groq API.")
        return None

def fetch_songs_by_mood(mood):
    try:
        query = f"{mood} hits"
        res = requests.get(f"{JIOSAAVN_API_URL}/search/songs", params={"query": query})
        data = res.json().get("data", {}).get("results", [])
        return data[:10]
    except Exception as e:
        st.error("Error fetching songs. Try again later.")
        return []

def show_song(song):
    # Display song name
    song_name = song.get("name", "Unknown Title")
    album_name = song.get("album", {}).get("name", "Unknown Album")
    st.subheader(song_name)
    st.text(f"Album: {album_name}")

    # Safe image display
    image_list = song.get("image", [])
    if isinstance(image_list, list) and len(image_list) > 0 and "link" in image_list[-1]:
        st.image(image_list[-1]["link"], width=300)
    else:
        st.warning(f"No image available for {song_name}.")

    # Safe audio playback
    audio_list = song.get("downloadUrl", [])
    if isinstance(audio_list, list) and len(audio_list) > 0 and "link" in audio_list[0]:
        st.audio(audio_list[0]["link"], format="audio/mp3")
    else:
        st.error(f"Audio unavailable for {song_name}.")

    # Attempt to fetch and display lyrics
    try:
        lyrics_res = requests.get(f"{JIOSAAVN_API_URL}/songs/{song['id']}/lyrics")
        lyrics = lyrics_res.json().get("data", {}).get("lyrics", "")
        if lyrics:
            with st.expander("🎤 Lyrics"):
                st.text(lyrics)
        else:
            st.info(f"Lyrics not available for {song_name}.")
    except Exception as e:
        st.warning(f"Could not fetch lyrics for {song_name}.")
        st.info(f"Error: {str(e)}")

# Mood detection and song loading
if st.button("🎵 Get Songs"):
    if mood_input.strip() == "":
        st.warning("Please enter your mood.")
    else:
        mood = get_mood_category(mood_input)
        if mood:
            st.success(f"Detected mood: {mood}")
            songs = fetch_songs_by_mood(mood)
            if songs:
                st.session_state.song_list = songs
                st.session_state.current_index = 0
            else:
                st.error("No songs found.")

# Navigation controls
if st.session_state.song_list:
    current = st.session_state.current_index
    show_song(st.session_state.song_list[current])

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏮ Previous", disabled=(current == 0)):
            st.session_state.current_index = max(0, current - 1)
    with col2:
        st.markdown("###")
        st.markdown("▶️ Now Playing")
    with col3:
        if st.button("⏭ Next", disabled=(current >= len(st.session_state.song_list) - 1)):
            st.session_state.current_index = min(len(st.session_state.song_list) - 1, current + 1)
