import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# Set up Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def classify_mood(text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a music assistant that classifies moods based on text."},
            {"role": "user", "content": f"Classify the user's mood from this text: {text}. Reply with one of: happy, sad, romantic, energetic, calm."}
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        res.raise_for_status()
        mood = res.json()["choices"][0]["message"]["content"].strip().lower()
        return mood
    except Exception as e:
        st.error("Failed to connect to Groq API.")
        st.exception(e)
        return None

def search_songs_jiosaavn(query):
    url = f"https://saavn.dev/api/search/songs?query={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        st.error("Error recommending songs.")
        st.exception(e)
        return []

def show_song(song):
    song_name = song.get("name") or song.get("song") or "Unknown Title"
    album_data = song.get("album", {})
    album_name = album_data.get("name", "Unknown Album")
    image_list = song.get("image") or []
    media_list = song.get("downloadUrl") or []

    st.subheader(song_name)
    st.caption(f"Album: {album_name}")

    # Show image safely
    image_url = ""
    if isinstance(image_list, list) and image_list:
        for img in reversed(image_list):
            if img.get("link"):
                image_url = img["link"]
                break
    if image_url:
        try:
            st.image(image_url, width=300)
        except Exception:
            st.warning("Image could not be loaded.")
    else:
        st.warning("No image available.")

    # Show audio player
    audio_url = ""
    if isinstance(media_list, list) and media_list:
        for audio in reversed(media_list):
            if audio.get("link"):
                audio_url = audio["link"]
                break
    if audio_url:
        st.audio(audio_url, format="audio/mp3")
    else:
        st.error(f"Audio unavailable for {song_name}. Please try another song.")

# UI
st.title("🎵 Mood-Based Music Recommender")
user_input = st.text_input("How are you feeling today?")

if user_input:
    mood = classify_mood(user_input)
    if mood:
        st.success(f"Detected mood: {mood}")
        song_results = search_songs_jiosaavn(mood)
        if song_results:
            for song in song_results[:10]:
                show_song(song)
        else:
            st.warning("No songs found for the selected mood. Please try again later.")
