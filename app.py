import streamlit as st
import requests
import os

# Function to fetch songs from JioSaavn API (Unofficial)
def fetch_songs(query):
    base_url = "https://saavn.dev/api"
    try:
        response = requests.get(f"{base_url}/search/songs", params={"query": query})
        data = response.json()
        return data['data']['results']  # List of song details
    except Exception as e:
        st.error(f"Error fetching songs: {e}")
        return []

# Function to show song details and audio player
def show_song(song):
    song_name = song.get("song", "Unknown Title")
    album_name = song.get("album", "Unknown Album")
    song_url = song.get("media_url", "")
    
    st.subheader(song_name)
    st.text(f"Album: {album_name}")
    
    # Display audio player if song URL is available
    if song_url:
        st.audio(song_url, format="audio/mp3")
    else:
        st.error(f"Audio unavailable for {song_name}. Please try another song.")

# Function to recommend songs based on mood
def recommend_songs(mood):
    # Make a request to Groq API for mood-based recommendations (replace with Groq API)
    groq_url = "https://api.groq.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    }
    data = {
        "model": "text-davinci-003",  # Example model; replace with the latest model from Groq
        "prompt": f"Recommend 10 songs for a {mood} mood.",
        "max_tokens": 200
    }
    try:
        response = requests.post(groq_url, headers=headers, json=data)
        response.raise_for_status()
        recommended_songs = response.json().get("choices", [])
        song_list = [song['text'] for song in recommended_songs]
        return song_list
    except Exception as e:
        st.error(f"Error recommending songs: {e}")
        return []

# Streamlit UI
st.title("Mood-based Music Streaming Platform")
mood = st.selectbox("Select your mood", ["Happy", "Sad", "Energetic", "Relaxed"])

# Recommend songs based on mood
if mood:
    st.subheader(f"Recommended songs for a {mood} mood:")
    song_list = recommend_songs(mood)
    
    if song_list:
        for song_name in song_list[:10]:  # Display up to 10 songs
            st.write(f"- {song_name}")
        
        # Play a song from the recommended list
        selected_song = st.selectbox("Choose a song to play", song_list)
        
        if selected_song:
            song_data = fetch_songs(selected_song)
            if song_data:
                show_song(song_data[0])  # Play the first song from the search results
            else:
                st.error(f"Could not find the song {selected_song}.")
    else:
        st.error("No songs found for the selected mood. Please try again later.")
