from flask import Flask, render_template, request, jsonify
import yt_dlp
from moviepy.editor import VideoFileClip
from openai import OpenAI
import os

# Initialize the client with your API key
client = OpenAI()

app = Flask(__name__)

# Function to handle transcription from ytchat.py
def transcribe_youtube_video(youtube_url):
    try:
        # Download YouTube video using yt_dlp
        ydl_opts = {
            'format': 'mp4/best',
            'outtmpl': 'temp_video.mp4',  # Output filename
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print("Download completed successfully.")

        # Convert the downloaded video to mp3
        video = VideoFileClip('temp_video.mp4')
        audio = video.audio
        audio.write_audiofile('output_audio.mp3')
        audio.close()
        print("Conversion completed successfully. Audio saved as 'output_audio.mp3'.")

        # Transcribe the audio file using OpenAI API
        with open("output_audio.mp3", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcription_text = transcription.text
            print("Transcription completed successfully.")
            return transcription_text
    except Exception as e:
        raise Exception(f"An error occurred during transcription: {e}")

# Function to handle chatbot interaction from ytchat.py
def ask_chatbot(context, user_question):
    try:
        # Messages list to hold the conversation history
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's questions based on the provided context."},
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": user_question}
        ]

        # Get the assistant's response using OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Updated to use the latest model
            messages=messages
        )
        assistant_response = completion.choices[0].message.content
        return assistant_response
    except Exception as e:
        raise Exception(f"An error occurred during chatbot interaction: {e}")

@app.route('/')
def index():
    return render_template('index.html')  # Load the UI page

@app.route('/transcribe', methods=['POST'])
def transcribe():
    youtube_url = request.form['youtube_url']
    try:
        # Call the function to transcribe the YouTube video
        transcribed_text = transcribe_youtube_video(youtube_url)
        return jsonify({'status': 'success', 'message': 'Transcription complete', 'context': transcribed_text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form['user_question']
    context = request.form['context']  # Load the context from the previous transcription
    try:
        # Call the chatbot function to answer the user's question
        response = ask_chatbot(context, user_question)
        return jsonify({'status': 'success', 'response': response})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
        app.run(debug=True)
