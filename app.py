import streamlit as st
import requests
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

# ENV Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
JIOSAAVN_API_URL = os.getenv("JIOSAAVN_API_URL", "https://saavn.dev/api")

# Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Moodify Music", layout="centered")
st.title("🎧 Moodify - Mood Based Music Recommender")

# Session state init
if "song_list" not in st.session_state:
    st.session_state.song_list = []
if "song_index" not in st.session_state:
    st.session_state.song_index = 0
if "current_song" not in st.session_state:
    st.session_state.current_song = {}

# Mood & Artist Input
with st.form("mood_form"):
    user_input = st.text_area("Describe how you're feeling:", "")
    artist_input = st.text_input("Optional: Favorite Artist or Band")
    submit = st.form_submit_button("🎵 Get Songs")

if submit and user_input:
    try:
        with st.spinner("Analyzing your mood..."):
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a music mood classifier."},
                    {"role": "user", "content": f"Classify the mood from: {user_input}. Only return one-word mood like Happy, Sad, Chill, Energetic, Romantic, etc."}
                ]
            )
            mood = response.choices[0].message.content.strip()
            st.success(f"Mood detected: {mood}")

        # Build query
        query = f"{mood} songs"
        if artist_input:
            query += f" by {artist_input}"

        with st.spinner(f"Searching JioSaavn for: {query}"):
            search = requests.get(f"{JIOSAAVN_API_URL}/search/songs", params={"query": query})
            data = search.json().get("data", {}).get("results", [])
            if isinstance(data, list) and data:
                st.session_state.song_list = data[:10]
                st.session_state.song_index = 0
                st.session_state.current_song = st.session_state.song_list[0]
            else:
                st.error("No songs found. Try a different mood or artist.")
    except Exception as e:
        st.error("❌ Failed to connect to Groq or JioSaavn API.")
        st.exception(e)

# Music Player UI
def show_song(song):
    st.subheader(song.get("name", "Unknown Title"))
    st.text(f"Album: {song.get('album', {}).get('name', 'Unknown')}")
    st.image(song.get("image", "")[-1]["link"], width=300)
    st.audio(song.get("downloadUrl", [{}])[0].get("link", ""), format="audio/mp3")

    # Show lyrics
    try:
        lyrics_res = requests.get(f"{JIOSAAVN_API_URL}/songs/{song['id']}/lyrics")
        lyrics = lyrics_res.json().get("data", {}).get("lyrics", "")
        if lyrics:
            with st.expander("🎤 Lyrics"):
                st.text(lyrics)
    except:
        pass

# Playback Controls
if st.session_state.song_list:
    current = st.session_state.song_index
    show_song(st.session_state.song_list[current])

    cols = st.columns(3)
    if cols[0].button("⏮️ Previous", disabled=current == 0):
        st.session_state.song_index = max(0, current - 1)
        st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]

    if cols[2].button("⏭️ Next", disabled=current >= len(st.session_state.song_list) - 1):
        st.session_state.song_index = min(len(st.session_state.song_list) - 1, current + 1)
        st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]
