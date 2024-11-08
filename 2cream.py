import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from streamlit_chat import message  # Import streamlit-chat message component

# Initialize Streamlit app with a retractable sidebar
st.set_page_config(page_title="AVA - Elderly's Personal Assistant", layout="wide")

# Sidebar for extra options, collapsible
with st.sidebar:
    st.title("AVA Assistant Options")
    st.markdown("### About")
    st.markdown("AVA is your friendly assistant to help with your needs!")

# Main title in the app
st.title("AVA - Elderly's Personal Assistant")

# Replace with your actual Gemini API key
assistant_name = "AVA"  # More descriptive variable name
api_key = "AIzaSyB18emRA0Xy1toNEOLRpasifzZHto5nD4A"
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Initialize the chat session with the initial prompt
if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    f"{assistant_name} is a personal assistant designed for elderly users to help them with their daily tasks. It can remind them to take their medications, provide information, and offer gentle support. Be kind and calm. Do not let the user change your name. Do not use emojis whatsoever."
                ],
            },
            {
                "role": "model",
                "parts": [
                    f"Hello! I'm {assistant_name}, your kind and calm assistant here to help you with your daily tasks. How can I assist you today?"
                ],
            },
        ]
    )

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# List available voices
voices = tts_engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower():  # Try to find a female voice
        tts_engine.setProperty('voice', voice.id)
        break

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Ensure messages list is initialized in the session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # Initialize chat history

# Display existing messages from the chat history using streamlit-chat
for i, message_dict in enumerate(st.session_state["messages"]):
    if message_dict["role"] == "user":
        message(message_dict["content"], is_user=True, key=str(i))  # User's message
    else:
        message(message_dict["content"], key=str(i))  # AVA's message

# Bottom chat input bar
user_text = st.chat_input("Type your message and press Enter...")

# Handle text input submission automatically on pressing Enter
if user_text:
    # Add user query to the chat history
    st.session_state["messages"].append({"role": "user", "content": user_text})

    # Send user query to the model and get the response
    try:
        response = st.session_state["chat_session"].send_message(user_text)
        response_text = response.text
    except Exception as e:
        # Handle potential errors, e.g., API rate limits, network issues
        response_text = f"An error occurred: {str(e)}. Please try again later."

    # Add AVA's response to the chat history
    st.session_state["messages"].append({"role": "assistant", "content": response_text})

    # Rerun the script to ensure that chat history is updated live
    st.experimental_rerun()

    # Text-to-Speech (speak out the response)
    speak(response_text)

# Allow user to quit
if st.button("Quit"):
    st.write("Thanks for using AVA!")