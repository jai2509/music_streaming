import streamlit as st
import requests

st.set_page_config(page_title="Mood-Based Music Player", layout="centered")

# JioSaavn API Base URL (Unofficial)
API_BASE_URL = "https://saavn.dev/api"

# Fetch songs by query
def fetch_songs(query):
    try:
        response = requests.get(f"{API_BASE_URL}/search/songs", params={"query": query})
        response.raise_for_status()
        results = response.json()
        return results.get("data", {}).get("results", [])
    except Exception as e:
        st.error(f"Error fetching songs: {e}")
        return []

# Show song with image and audio
def show_song(song):
    song_name = song.get("name") or song.get("song") or "Unknown Title"
    album_data = song.get("album", {})
    album_name = album_data.get("name", "Unknown Album")
    image = song.get("image") or []
    media_url = song.get("downloadUrl", [])
    
    st.subheader(song_name)
    st.caption(f"Album: {album_name}")

    if image and isinstance(image, list):
        st.image(image[-1].get("link", ""), width=300)
    else:
        st.warning("No image available.")

    if media_url and isinstance(media_url, list):
        audio_url = media_url[-1].get("link", "")
        if audio_url:
            st.audio(audio_url, format="audio/mp3")
        else:
            st.error(f"Audio unavailable for {song_name}. Please try another song.")
    else:
        st.error(f"Audio unavailable for {song_name}. Please try another song.")

# Recommend songs based on mood
def recommend_songs(mood):
    mood_song_map = {
        "Happy": ["Happy by Pharrell Williams", "Uptown Funk by Mark Ronson", "Can't Stop the Feeling!"],
        "Sad": ["Someone Like You by Adele", "Fix You by Coldplay", "The Night We Met by Lord Huron"],
        "Energetic": ["Eye of the Tiger by Survivor", "Stronger by Kanye West", "Thunderstruck by AC/DC"],
        "Relaxed": ["Sunset Lover by Petit Biscuit", "Night Owl by Galimatias", "Weightless by Marconi Union"]
    }
    return mood_song_map.get(mood, [])

# --- Streamlit UI ---
st.title("🎧 Mood-Based Music Player")
st.markdown("Choose your mood and enjoy music that matches your vibe!")

mood = st.selectbox("Select Your Mood", ["Happy", "Sad", "Energetic", "Relaxed"])

if mood:
    recommended = recommend_songs(mood)
    st.markdown("#### Recommended Songs:")
    for i, song in enumerate(recommended, 1):
        st.markdown(f"{i}. {song}")

    selected = st.selectbox("Pick a song to play", recommended)

    if selected:
        with st.spinner(f"Searching for: {selected}..."):
            search_results = fetch_songs(selected)
            if search_results:
                show_song(search_results[0])
            else:
                st.error("No results found for the selected song.")
