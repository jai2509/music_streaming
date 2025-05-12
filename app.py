import streamlit as st
import requests

# Function to search JioSaavn with mood
def search_jiosaavn_song(query, mood=None):
    url = f"https://saavn.dev/search/songs?query={query}"
    if mood:
        url += f"&mood={mood}"  # Add mood-based query (if supported by the API)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("results", [])
    return []

# Function to search iTunes with mood (limited to song names, so we will filter by mood manually)
def search_itunes_song(query, mood=None):
    url = f"https://itunes.apple.com/search?term={query}&media=music&limit=10"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    return []

# Streamlit UI
st.title("🎵 Mood-based Music Player")

# Mood filter options
moods = ["Happy", "Relaxed", "Energetic", "Sad", "Chill", "Party"]
selected_mood = st.selectbox("Select a Mood:", moods)

# User input for song or artist (optional if you want to allow searching specific genre)
query = st.text_input("Enter a song, artist, or genre:")

# Queue system for songs
if "queue" not in st.session_state:
    st.session_state.queue = []  # Initialize the queue
if "current_song" not in st.session_state:
    st.session_state.current_song = None  # Track the current song being played

# Function to play audio from the queue
def play_audio(url):
    st.session_state.current_song = url
    st.audio(url, format="audio/mp3")

# Function to update the queue
def add_to_queue(songs):
    st.session_state.queue.extend(songs)

# Adding songs to the queue based on user query and mood
if query:
    # Search JioSaavn
    st.subheader("🎶 JioSaavn Results:")
    jio_songs = search_jiosaavn_song(query, selected_mood)
    if jio_songs:
        add_to_queue(jio_songs)  # Add to queue
        for song in jio_songs:
            st.write(f"**{song['name']}** by {song['primaryArtists']}")
            audio_link = song.get("downloadUrl", [])[-1].get("link", "")
            if audio_link:
                st.button(f"Add {song['name']} to Queue", on_click=play_audio, args=(audio_link,))
            else:
                st.write("Audio unavailable for this song.")
    else:
        st.write("No songs found on JioSaavn.")

    # Search iTunes
    st.subheader("🎧 iTunes Results:")
    itunes_songs = search_itunes_song(query, selected_mood)
    if itunes_songs:
        add_to_queue(itunes_songs)  # Add to queue
        for song in itunes_songs:
            st.write(f"**{song['trackName']}** by {song['artistName']}")
            preview_url = song.get("previewUrl", "")
            if preview_url:
                st.button(f"Add {song['trackName']} to Queue", on_click=play_audio, args=(preview_url,))
            else:
                st.write("Preview unavailable for this song.")
    else:
        st.write("No songs found on iTunes.")

# Display current song and queue
if st.session_state.queue:
    st.subheader("🎶 Now Playing:")
    song = st.session_state.current_song
    if song:
        st.audio(song, format="audio/mp3")
    
    st.subheader("🎵 Queue:")
    for idx, song in enumerate(st.session_state.queue):
        st.write(f"{idx + 1}. {song['name'] if 'name' in song else song['trackName']}")

# Auto play functionality (if the current song finishes, play the next in queue)
def auto_play():
    if st.session_state.queue:
        next_song = st.session_state.queue.pop(0)
        st.session_state.queue.append(next_song)  # Loop song at the end of the queue
        play_audio(next_song)

auto_play()  # Automatically play next song in queue after the current one finishes
