import os
import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Key
groq_api_key = os.getenv("GROQ_API_KEY")

def detect_mood(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that categorizes moods."},
            {"role": "user", "content": f"Based on this message, choose one mood from the following list: happy, sad, romantic, party, workout, chill, energetic, devotional, patriotic, relaxing. Message: {text}. Reply with only one mood from the list."}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        return result['choices'][0]['message']['content'].strip().lower()
    except Exception as e:
        st.error(f"Error detecting mood: {e}")
        return None

def fetch_songs_by_mood(mood):
    try:
        url = f"https://saavn.dev/search/songs?query={mood}"
        response = requests.get(url)
        data = response.json()
        return data.get("data", {}).get("results", [])
    except Exception as e:
        st.error(f"Error fetching songs: {e}")
        return []

def show_song(song):
    title = song.get("name", "Unknown Title")
    album = song.get("album", {})
    image = song.get("image", [])
    url = song.get("url", "")
    download_url = song.get("downloadUrl", [])

    st.subheader(title)
    st.markdown(f"**Album**: {album.get('name', 'N/A')}  ")
    st.markdown(f"**URL**: [Listen on JioSaavn]({url})")

    try:
        if image:
            st.image(image[-1].get("link", ""), width=300)
        else:
            st.warning("No image available.")
    except Exception as e:
        st.warning("Image display error.")

    if download_url:
        audio_url = download_url[-1].get("link", "")
        if audio_url:
            st.audio(audio_url)
        else:
            st.warning("Audio unavailable.")
    else:
        st.warning("Audio unavailable.")

# Streamlit UI
st.title("🎵 Mood-Based Music Recommender")
user_input = st.text_input("How are you feeling today?")

if user_input:
    mood = detect_mood(user_input)
    if mood:
        st.info(f"Detected Mood: {mood}")
        song_results = fetch_songs_by_mood(mood)

        if song_results:
            for song in song_results[:10]:
                show_song(song)
        else:
            fallback_moods = {
                "happy": ["Pharrell Williams - Happy", "Justin Timberlake - Can't Stop The Feeling"],
                "sad": ["Fix You - Coldplay", "Someone Like You - Adele"],
                "romantic": ["Perfect - Ed Sheeran", "Tum Hi Ho - Aashiqui 2"],
                "party": ["Uptown Funk", "Taki Taki"],
                "relaxing": ["Weightless - Marconi Union", "Let Her Go - Passenger"]
            }
            if mood in fallback_moods:
                st.warning("No songs found for this mood. Showing fallback suggestions:")
                for song_name in fallback_moods[mood]:
                    st.markdown(f"🎶 {song_name}")
            else:
                st.warning("No songs found for the selected mood.")
