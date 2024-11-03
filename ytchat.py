import yt_dlp
from moviepy.editor import VideoFileClip
from openai import OpenAI
import re
import os

# Initialize the client with your API key
client = OpenAI()

def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

# Function to download a YouTube video in mp4 format and return the filename
def download_yt_video(url):
    """Downloads a YouTube video in mp4 format with a unique filename."""
    try:
        video_id = get_video_id(url)
        if not video_id:
            print("Invalid YouTube URL.")
            return None
        
        # Define a unique filename using the video ID
        output_filename = f"temp_video_{video_id}.mp4"
        
        ydl_opts = {
            'format': 'mp4/best',
            'outtmpl': output_filename,    # Unique filename based on video ID
            'noplaylist': True,            # Download only the video, not the playlist
            'nocheckcertificate': True,    # Bypass SSL certificate check
            'force_overwrites': True       # Force overwrite if the file exists
        }
        
        # Clear cache to avoid using old metadata
        with yt_dlp.YoutubeDL() as ydl:
            ydl.cache.remove()

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print(f"Download completed successfully. File saved as {output_filename}")
        return output_filename  # Return the unique filename for further use
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to convert mp4 to mp3
def convert_mp4_to_mp3(mp4_filename):
    """Converts an mp4 video file to an mp3 audio file."""
    try:
        video = VideoFileClip(mp4_filename)
        audio = video.audio
        audio.write_audiofile("output_audio.mp3")  # Save as a consistent filename for transcription
        audio.close()
        print("Audio extracted and saved as 'output_audio.mp3'.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to transcribe audio to text
def transcribe_audio_to_text():
    """Transcribes the 'output_audio.mp3' file using OpenAI API and saves to 'transcription.txt'."""
    try:
        with open("output_audio.mp3", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            with open("transcription.txt", "w", encoding='utf8') as text_file:
                text_file.write(transcription.text)
            print("Transcription completed successfully.")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")

# Main function to run the complete process
def process_youtube_video(url):
    # Step 1: Download video
    video_filename = download_yt_video(url)
    if not video_filename:
        print("Failed to download video.")
        return

    # Step 2: Convert downloaded video to mp3
    convert_mp4_to_mp3(video_filename)
    
    # Step 3: Transcribe the audio
    transcribe_audio_to_text()

# Example usage
if __name__ == "__main__":
    url = input("Please enter the YouTube video URL: ")
    process_youtube_video(url)
