from openai import OpenAI
import os

# Initialize the client with your API key
client = OpenAI()

# Read prompt from a file
with open('transcription.txt', 'r', encoding='utf8') as file:
    transcription_text = file.read().strip()  # Strip any trailing newline or spaces

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
                model="gpt-4o", 
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

