import yt_dlp
from moviepy.editor import VideoFileClip
from openai import OpenAI
import os

# Initialize the client with your API key
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Function to download a YouTube video in mp4 format
def download_yt_video(url):
    """
    Downloads a YouTube video in mp4 format with the filename 'temp_video.mp4'.
    
    Parameters:
    url (str): The URL of the YouTube video.
    
    Returns:
    None
    """
    try:
        ydl_opts = {
            'format': 'mp4/best',
            'outtmpl': 'temp_video.mp4',  # Output filename
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to convert mp4 to mp3
def convert_mp4_to_mp3(mp4_filename, mp3_filename):
    """
    Converts an mp4 video file to an mp3 audio file.
    
    Parameters:
    mp4_filename (str): The name of the mp4 file to be converted.
    mp3_filename (str): The desired output mp3 filename.
    
    Returns:
    None
    """
    try:
        # Load the video file
        video = VideoFileClip(mp4_filename)
        
        # Extract audio from the video
        audio = video.audio
        
        # Write the audio to an mp3 file
        audio.write_audiofile(mp3_filename)
        
        # Close the audio to release resources
        audio.close()
        print(f"Conversion completed successfully. Audio saved as '{mp3_filename}'.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Define the URL for the YouTube video
url = 'https://youtu.be/m7DcS5Hocrc'

# Call the function with the URL variable
download_yt_video(url)

# Convert the downloaded video to mp3
convert_mp4_to_mp3('temp_video.mp4', 'output_audio.mp3')

# Transcribe the audio file using OpenAI API
audio_file = open("output_audio.mp3", "rb")
try:
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    # Save the transcription to a .txt file
    with open("transcription.txt", "w", encoding='utf8') as text_file:
        text_file.write(transcription.text)
    transcription_text = transcription.text
    print("Transcription completed successfully.")
except Exception as e:
    print(f"An error occurred during transcription: {e}")
    transcription_text = ""
finally:
    audio_file.close()

# Function to start and maintain an ongoing conversation
def ongoing_conversation(transcription_text):
    """
    Start a conversation with GPT-4o, maintaining the conversation history efficiently.
    
    Parameters:
    transcription_text (str): The initial context for the assistant to refer to.
    
    Returns:
    None
    """
    # Messages list to hold the conversation history
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer the user's questions based on the provided context."},
        {"role": "system", "content": f"Context: {transcription_text}"}
    ]

    print("Chat with GPT-4o. Type 'exit', 'quit', or 'bye' to end the conversation.")
    while True:
        # Get user input
        user_input = input("You: ")

        # Check if the user wants to exit
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("GPT-4o: Goodbye!")
            break

        # Append the user's message to the conversation history
        messages.append({"role": "user", "content": user_input})

        # Get the assistant's response using OpenAI API
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Updated to use the latest model
                messages=messages
            )

            # Extract the response
            assistant_response = completion.choices[0].message.content
            print(f"GPT-4o: {assistant_response}")

            # Append the assistant's response to the conversation history
            messages.append({"role": "assistant", "content": assistant_response})

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    ongoing_conversation(transcription_text)
