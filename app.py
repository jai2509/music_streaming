import os
import streamlit as st
import requests
from dotenv import load_dotenv
from groq import Groq

# Load .env variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JIOSAAVN_API_URL = os.getenv("JIOSAAVN_API_URL", "https://saavn.dev")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Streamlit UI
st.set_page_config(page_title="🎵 Mood-Based Music Player", layout="centered")
st.title("🎵 Mood-Based Music Player")
st.markdown("Enter your mood description, and get Bollywood + Hollywood songs to match!")

# Mood Input
user_input = st.text_input("Describe how you're feeling:", placeholder="e.g. I'm feeling calm and relaxed...")

# Playback session state
if 'current_song' not in st.session_state:
    st.session_state.current_song = None
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0
if 'song_list' not in st.session_state:
    st.session_state.song_list = []

# Mood detection + fetch songs
if st.button("🎧 Get Songs for My Mood"):
    if user_input.strip() == "":
        st.warning("Please describe your mood.")
    else:
        with st.spinner("Analyzing your mood with Groq..."):
            prompt = f"Classify this mood into one of: Happy, Sad, Energetic, Calm.\nMood: {user_input}\nMood:"
            response = groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=10
            )
            mood = response.choices[0].message.content.strip()
            st.success(f"Detected mood: **{mood}**")

        with st.spinner(f"Fetching {mood}-themed songs from JioSaavn..."):
            search = requests.get(f"{JIOSAAVN_API_URL}/search/songs", params={"query": mood})
            if search.status_code == 200 and search.json().get("data"):
                results = search.json()["data"]
                st.session_state.song_list = results[:10]  # Store top 10 songs
                st.session_state.song_index = 0
                st.session_state.current_song = st.session_state.song_list[0]
            else:
                st.error("No songs found for this mood. Try another mood description.")

# Show current song
if st.session_state.current_song:
    song = st.session_state.current_song
    st.subheader(f"🎶 Now Playing: {song['name']} - {song['primaryArtists']}")
    audio_link = song['downloadUrl'][-1]['link'] if song.get('downloadUrl') else None

    if audio_link:
        st.audio(audio_link, format="audio/mp3")
    else:
        st.warning("Audio not available.")

    # Navigation Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.song_index == 0):
            st.session_state.song_index -= 1
            st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]
    with col2:
        if st.button("➡️ Next", disabled=st.session_state.song_index == len(st.session_state.song_list) - 1):
            st.session_state.song_index += 1
            st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]
