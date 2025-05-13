import streamlit as st
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import random
import time

# Load environment variables
load_dotenv()

# Retrieve YouTube API key from .env
api_key = os.getenv('YOUTUBE_API_KEY')

# Build the YouTube API client
youtube = build("youtube", "v3", developerKey=api_key)

# Function to search YouTube
def search_youtube(query):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        videoCategoryId="10",  # Music category
        maxResults=5
    )
    response = request.execute()
    return response['items']

# Initialize session state for song queue and current song
if 'song_queue' not in st.session_state:
    st.session_state.song_queue = []
    st.session_state.current_song = 0
    st.session_state.is_playing = False

# Function to display the current song
def show_song(song):
    title = song['snippet']['title']
    video_id = song['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    thumbnail_url = song['snippet']['thumbnails']['high']['url']
    
    st.write(f"### Now Playing: {title}")
    st.image(thumbnail_url, width=300)
    st.video(video_url)  # Play the video directly in Streamlit

# Play next song in the queue
def play_next():
    if st.session_state.current_song < len(st.session_state.song_queue) - 1:
        st.session_state.current_song += 1
    else:
        st.session_state.current_song = 0  # Loop to the first song

# Play previous song in the queue
def play_previous():
    if st.session_state.current_song > 0:
        st.session_state.current_song -= 1
    else:
        st.session_state.current_song = len(st.session_state.song_queue) - 1  # Loop to the last song

# Handle mood selection
mood = st.selectbox("Select Mood", ["Bhangra", "Chill", "Workout", "Romantic", "Jazz"])

# Search for songs based on the selected mood
if mood:
    st.session_state.song_queue = search_youtube(mood)
    if st.session_state.song_queue:
        st.write(f"Found {len(st.session_state.song_queue)} songs for mood: {mood}")
    else:
        st.write("No songs found for this mood. Please try again later.")
    
    # Show the current song if available
    if st.session_state.song_queue:
        show_song(st.session_state.song_queue[st.session_state.current_song])

# Controls to play next or previous song
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Previous", key="previous"):
        play_previous()
        show_song(st.session_state.song_queue[st.session_state.current_song])

with col2:
    if st.button("Play", key="play"):
        if not st.session_state.is_playing:
            st.session_state.is_playing = True
            show_song(st.session_state.song_queue[st.session_state.current_song])

with col3:
    if st.button("Next", key="next"):
        play_next()
        show_song(st.session_state.song_queue[st.session_state.current_song])

