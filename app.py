import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Groq API setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.title("🎧 Mood-Based Music Recommender")

def detect_mood(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"Based on this message, identify the user's mood (e.g., happy, sad, relaxed, energetic): {text}"

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        mood = response.json()["choices"][0]["message"]["content"].strip().lower()
        return mood
    except Exception as e:
        st.error(f"Failed to connect to Groq API: {e}")
        return None

def fetch_songs_by_mood(mood):
    try:
        res = requests.get(f"https://saavn.dev/search/songs?query={mood}")
        data = res.json()
        return data.get("data", [])[:10]
    except Exception as e:
        st.error(f"Error fetching songs: {e}")
        return []

def show_song(song):
    title = song.get("name", "Unknown Title")
    artists = ", ".join(song.get("artists", [])) if song.get("artists") else "Unknown Artist"
    image = song.get("image", [])
    audio_url = song.get("downloadUrl", [])

    st.markdown(f"### 🎵 {title}")
    st.write(f"**Artists:** {artists}")

    if image and isinstance(image, list):
        link = image[-1].get("link", "")
        if link:
            st.image(link, width=300)
        else:
            st.warning("No image available.")
    else:
        st.warning("No image available.")

    if audio_url and isinstance(audio_url, list):
        url = audio_url[-1].get("link", "")
        if url:
            st.audio(url)
        else:
            st.warning("Audio unavailable.")
    else:
        st.warning("Audio unavailable.")

user_input = st.text_input("How are you feeling today?")

if st.button("Recommend Songs"):
    if user_input:
        mood = detect_mood(user_input)
        if mood:
            st.success(f"Mood detected: {mood}")
            song_results = fetch_songs_by_mood(mood)
            if song_results:
                for song in song_results:
                    show_song(song)
                    st.markdown("---")
            else:
                st.warning("No songs found for the selected mood.")
        else:
            st.error("Could not determine your mood.")
    else:
        st.warning("Please enter your current feeling.")
