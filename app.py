import os
import streamlit as st
import requests
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JIOSAAVN_API_URL = os.getenv("JIOSAAVN_API_URL", "https://saavn.dev")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Streamlit config
st.set_page_config(page_title="🎵 Mood-Based Music Player", layout="centered")
st.title("🎵 Mood-Based Music Player")
st.markdown("Enter your mood to get Bollywood + Hollywood songs!")

# Input field
user_input = st.text_input("How are you feeling today?", placeholder="e.g. I'm feeling energetic...")

# Session state
if "current_song" not in st.session_state:
    st.session_state.current_song = None
if "song_index" not in st.session_state:
    st.session_state.song_index = 0
if "song_list" not in st.session_state:
    st.session_state.song_list = []

# Get songs based on mood
if st.button("🎧 Get Songs"):
    if user_input.strip() == "":
        st.warning("Please enter a mood description.")
    else:
        with st.spinner("Detecting mood using Groq..."):
            try:
                prompt = f"Classify this mood into one of: Happy, Sad, Energetic, Calm.\nMood: {user_input}\nMood:"
                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",  # ✅ Updated working model
                    messages=[
                        {"role": "system", "content": "You are a mood classification assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=10
                )
                mood = response.choices[0].message.content.strip()
                st.success(f"Detected mood: **{mood}**")

                # Fetch songs from JioSaavn
                with st.spinner(f"Searching for {mood} songs..."):
                    search = requests.get(f"{JIOSAAVN_API_URL}/search/songs", params={"query": mood})
                    data = search.json().get("data", [])
                    if data:
                        st.session_state.song_list = data[:10]
                        st.session_state.song_index = 0
                        st.session_state.current_song = st.session_state.song_list[0]
                    else:
                        st.error("No songs found. Try a different mood.")
            except Exception as e:
                st.error("Failed to connect to Groq API.")
                st.exception(e)

# Show current song
if st.session_state.current_song:
    song = st.session_state.current_song
    st.subheader(f"🎶 Now Playing: {song['name']} - {song['primaryArtists']}")
    audio_link = song.get("downloadUrl", [{}])[-1].get("link")

    if audio_link:
        st.audio(audio_link, format="audio/mp3")
    else:
        st.warning("Audio preview unavailable.")

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.song_index == 0):
            st.session_state.song_index -= 1
            st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]
    with col2:
        if st.button("➡️ Next", disabled=st.session_state.song_index == len(st.session_state.song_list) - 1):
            st.session_state.song_index += 1
            st.session_state.current_song = st.session_state.song_list[st.session_state.song_index]
