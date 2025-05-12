import streamlit as st
import requests

# Function to search JioSaavn
def search_jiosaavn_song(query):
    url = f"https://saavn.dev/search/songs?query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("results", [])
    return []

# Function to search iTunes
def search_itunes_song(query):
    url = f"https://itunes.apple.com/search?term={query}&media=music&limit=5"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    return []

# Streamlit UI
st.title("🎵 Music Search App")

# User input for song or artist
query = st.text_input("Enter a song or artist name:")

# Keep track of the audio URL
if "audio_url" not in st.session_state:
    st.session_state.audio_url = None

# Function to stop the previous audio and play the new one
def play_audio(url):
    if st.session_state.audio_url != url:
        st.session_state.audio_url = url
        st.audio(url, format="audio/mp3", use_buffer=True)

if query:
    # Search JioSaavn
    st.subheader("🎶 JioSaavn Results:")
    jio_songs = search_jiosaavn_song(query)
    if jio_songs:
        for song in jio_songs:
            st.write(f"**{song['name']}** by {song['primaryArtists']}")
            # Full audio link from JioSaavn
            audio_link = song.get("downloadUrl", [])[-1].get("link", "")
            if audio_link:
                if st.button(f"Play {song['name']} from JioSaavn"):
                    play_audio(audio_link)
            else:
                st.write("Audio unavailable for this song.")
    else:
        st.write("No songs found on JioSaavn.")

    # Search iTunes
    st.subheader("🎧 iTunes Results:")
    itunes_songs = search_itunes_song(query)
    if itunes_songs:
        for song in itunes_songs:
            st.write(f"**{song['trackName']}** by {song['artistName']}")
            # Audio Preview from iTunes (30 seconds)
            preview_url = song.get("previewUrl", "")
            if preview_url:
                if st.button(f"Play Preview of {song['trackName']} from iTunes"):
                    play_audio(preview_url)
            else:
                st.write("Preview unavailable for this song.")
    else:
        st.write("No songs found on iTunes.")
