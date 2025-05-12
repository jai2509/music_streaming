import streamlit as st
import requests
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set up Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Streamlit UI
st.title("🎵 Mood-Based Music Recommender")
st.write("Tell us how you feel, and we'll find songs that match your mood!")

# User input
user_input = st.text_input("How are you feeling today?", "I'm feeling energetic and happy")

# Function to detect mood using Groq
def detect_mood(text):
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies the user's mood."},
                {"role": "user", "content": f"Classify the mood of this text: '{text}'. Only return one keyword such as happy, sad, energetic, romantic, calm, etc."}
            ],
            model="llama3-8b-8192"
        )
        mood = response.choices[0].message.content.strip().lower()
        return mood
    except Exception as e:
        st.error(f"Failed to detect mood: {e}")
        return None

# Function to fetch songs from JioSaavn
def fetch_songs_by_mood(mood):
    try:
        query = mood + " songs"
        url = f"https://saavn.dev/api/search/songs?query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            songs = data.get("data", {}).get("results", [])
            return songs
        else:
            st.warning(f"JioSaavn API request failed: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Failed to fetch songs: {e}")
        return []

# Function to display song
def show_song(song):
    st.subheader(song.get("name", "Unknown Title"))
    image = song.get("image")
    if image and isinstance(image, list):
        st.image(image[-1].get("link", ""), width=300)
    else:
        st.warning("No image available.")

    preview_url = song.get("downloadUrl", [{}])[-1].get("link")
    if preview_url:
        st.audio(preview_url)
    else:
        st.warning("Audio unavailable.")

    st.caption(f"Album: {song.get('album', {}).get('name', 'Unknown')}")
    st.markdown(f"[Listen More]({song.get('url', '#')})")

# Detect mood
if user_input:
    user_mood = detect_mood(user_input)
    if user_mood:
        st.success(f"Detected mood: {user_mood}")

        song_results = fetch_songs_by_mood(user_mood)

        if song_results:
            for song in song_results[:10]:
                show_song(song)
                st.markdown("---")
        else:
            st.warning("No songs found for the selected mood. Please try again later.")
