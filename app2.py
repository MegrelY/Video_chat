from flask import Flask, render_template, request, jsonify
import yt_dlp
from moviepy.editor import VideoFileClip
from openai import OpenAI
import re
import os

# Initialize the client with your API key
client = OpenAI()

app = Flask(__name__)

def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

# Function to download a YouTube video and return the filename
def download_yt_video(url):
    """Downloads a YouTube video and returns the unique filename."""
    try:
        video_id = get_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL.")
        
        output_filename = f"temp_video_{video_id}.mp4"
        
        ydl_opts = {
            'format': 'mp4/best',
            'outtmpl': output_filename,
            'noplaylist': True,
            'nocheckcertificate': True,
            'force_overwrites': True
        }

        # Clear cache to avoid using old metadata
        with yt_dlp.YoutubeDL() as ydl:
            ydl.cache.remove()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"Download completed successfully. File saved as {output_filename}")
        return output_filename  # Return the unique filename for further use

    except Exception as e:
        raise Exception(f"An error occurred during download: {e}")

# Function to convert mp4 to mp3
def convert_mp4_to_mp3(mp4_filename):
    """Converts an mp4 video file to an mp3 audio file."""
    try:
        video = VideoFileClip(mp4_filename)
        audio = video.audio
        audio.write_audiofile("output_audio.mp3")
        audio.close()
        print("Audio extracted and saved as 'output_audio.mp3'.")
    except Exception as e:
        raise Exception(f"An error occurred during conversion: {e}")

def transcribe_audio_to_text():
    """Transcribes 'output_audio.mp3' using OpenAI API and saves to 'transcription.txt'."""
    try:
        with open("output_audio.mp3", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            # Clear the previous content of 'transcription.txt' and save the new transcription
            with open("transcription.txt", "w", encoding='utf8') as text_file:
                text_file.write(transcription.text)
            print("Transcription completed successfully. New transcription saved.")
          #  print("Transcription Text:", transcription.text)  # Log transcription for verification
    except Exception as e:
        print(f"An error occurred during transcription: {e}")


# Flask route to handle transcription requests
@app.route('/transcribe', methods=['POST'])
def transcribe():
    youtube_url = request.form['youtube_url']
    try:
        # Step 1: Download the video
        video_filename = download_yt_video(youtube_url)
        
        # Step 2: Convert video to mp3
        convert_mp4_to_mp3(video_filename)
        
        # Step 3: Transcribe the audio
        transcribed_text = transcribe_audio_to_text()
        
        return jsonify({'status': 'success', 'message': 'Transcription complete', 'context': transcribed_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Flask route to handle chatbot interaction requests
@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['user_question']
    context = request.form['context']  # Load the context from the previous transcription
    try:
        # Messages list to hold the conversation history
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user’s questions based on the provided context."},
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": user_question}
        ]

        # Get the assistant’s response using OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages
        )
        assistant_response = completion.choices[0].message.content
        return jsonify({'status': 'success', 'response': assistant_response})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
@app.route('/')
def index():
    return render_template('index.html')  # This will look for index.html in the templates folder

if __name__ == '__main__':
    app.run(debug=True)
