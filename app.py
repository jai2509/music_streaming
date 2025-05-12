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

# Function to recommend songs based on mood (Mockup)
def recommend_songs(mood):
    mood_song_mapping = {
        "Happy": ["Happy by Pharrell Williams", "Can't Stop the Feeling! by Justin Timberlake", "Uptown Funk by Mark Ronson"],
        "Sad": ["Someone Like You by Adele", "Fix You by Coldplay", "The Night We Met by Lord Huron"],
        "Energetic": ["Stronger by Kanye West", "Lose Yourself by Eminem", "Till I Collapse by Eminem"],
        "Relaxed": ["Weightless by Marconi Union", "Sunset Lover by Petit Biscuit", "Night Owl by Galimatias"]
    }
    return mood_song_mapping.get(mood, [])

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
