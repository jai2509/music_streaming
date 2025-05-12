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

# Streamlit UI setup
st.set_page_config(page_title="🎵 Mood-based Music Player", page_icon="🎶", layout="wide")

# Title and Mood Filter
st.title("🎶 Mood-based Music Player")
moods = ["Happy", "Relaxed", "Energetic", "Sad", "Chill", "Party"]
selected_mood = st.selectbox("Select a Mood:", moods)

# Input for song search (genre, artist, or song)
query = st.text_input("Enter a song, artist, or genre:")

# Queue system
if "queue" not in st.session_state:
    st.session_state.queue = []  # Initialize the queue
if "current_song_index" not in st.session_state:
    st.session_state.current_song_index = 0  # Start at the first song

# Function to play audio
def play_audio(audio_url):
    st.session_state.current_song = audio_url
    st.audio(audio_url, format="audio/mp3")

# Function to add songs to the queue
def add_to_queue(songs):
    for song in songs:
        if 'downloadUrl' in song and song['downloadUrl']:
            audio_url = song['downloadUrl'][0].get('link', '')
        else:
            audio_url = ""
        
        if audio_url:
            st.session_state.queue.append(audio_url)

# Add songs to queue based on user query and mood
if query:
    # Search JioSaavn
    st.subheader("🎶 JioSaavn Results:")
    jio_songs = search_jiosaavn_song(query, selected_mood)
    if jio_songs:
        add_to_queue(jio_songs)
        for idx, song in enumerate(jio_songs):
            song_name = song.get('name', 'Unknown Song')
            artist = song.get('primaryArtists', 'Unknown Artist')
            cover_image = song.get('image', [])
            audio_url = song.get("downloadUrl", [])[-1].get("link", "")
            st.write(f"**{song_name}** by {artist}")
            if cover_image:
                st.image(cover_image[0].get("link", ""), width=100)
            if audio_url:
                st.button(f"Play {song_name}", on_click=play_audio, args=(audio_url,), key=f"jiosaavn_button_{idx}")
    else:
        st.write("No songs found on JioSaavn.")

    # Search iTunes
    st.subheader("🎧 iTunes Results:")
    itunes_songs = search_itunes_song(query, selected_mood)
    if itunes_songs:
        add_to_queue(itunes_songs)
        for idx, song in enumerate(itunes_songs):
            song_name = song.get("trackName", "Unknown Song")
            artist = song.get("artistName", "Unknown Artist")
            preview_url = song.get("previewUrl", "")
            cover_image = song.get("artworkUrl100", "")
            if preview_url:
                st.write(f"**{song_name}** by {artist}")
                if cover_image:
                    st.image(cover_image, width=100)
                st.button(f"Play {song_name}", on_click=play_audio, args=(preview_url,), key=f"itunes_button_{idx}")
    else:
        st.write("No songs found on iTunes.")

# UI for the currently playing song
if st.session_state.queue:
    song = st.session_state.queue[st.session_state.current_song_index]
    st.subheader("🎶 Now Playing:")
    st.write(f"**{song}**")  # Add artist/album info here if available
    st.audio(song, format="audio/mp3")

    # Player Controls (Next, Previous, Pause)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⏮ Previous", key="previous"):
            if st.session_state.current_song_index > 0:
                st.session_state.current_song_index -= 1
                play_audio(st.session_state.queue[st.session_state.current_song_index])
    
    with col2:
        if st.button("⏸ Pause", key="pause"):
            st.session_state.current_song = None
            st.audio("", format="audio/mp3")  # Stop current audio (pause)
    
    with col3:
        if st.button("⏭ Next", key="next"):
            if st.session_state.current_song_index < len(st.session_state.queue) - 1:
                st.session_state.current_song_index += 1
                play_audio(st.session_state.queue[st.session_state.current_song_index])

    # Display the queue
    st.subheader("🎵 Queue:")
    for idx, song in enumerate(st.session_state.queue):
        st.write(f"{idx + 1}. {song}")
    
    # Auto-play next song after current song finishes
    def auto_play():
        if st.session_state.current_song is None and len(st.session_state.queue) > 0:
            st.session_state.current_song_index += 1
            if st.session_state.current_song_index < len(st.session_state.queue):
                play_audio(st.session_state.queue[st.session_state.current_song_index])

    auto_play()  # Automatically play next song when the current one finishes

