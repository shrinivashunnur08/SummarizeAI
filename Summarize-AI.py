import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

load_dotenv()  # Load all the environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """
You are a YouTube video summarizer. Your task is to read the provided transcript and create a concise summary of the video's content in English. Please condense the key points and main ideas into a list of bullet points, ensuring the summary is no longer than 500-1500 words. Use clear and precise language. 
Note: Even if the transcript is in Hindi, Marathi, Tamil, Kannada, or any other language, the summary should be in English.
"""

# Function to get transcript in the specified language
def extract_transcript_details(youtube_video_url, language='en'):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript([language])
        transcript_text = transcript.fetch()

        transcript_combined = " ".join([i["text"] for i in transcript_text])

        return transcript_combined

    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception as e:
        raise e

# Function to get summary from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + "\n\n" + transcript_text)
    return response.text

st.title("Welcome to Shree's Summarize-AI App 🤖")
youtube_link = st.text_input("Enter the YouTube video link: (Ensure the URL contains characters up to the '&' symbol, but does not include the '&' itself)")

language = st.selectbox("Select Transcript Language", ["English", "Hindi", "Marathi", "Tamil", "Kannada"])
language_code = {
    'English': 'en',
    'Hindi': 'hi',
    'Marathi': 'mr',
    'Tamil': 'ta',
    'Kannada': 'kn'
}[language]

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Summarize 📃"):
    transcript_text = extract_transcript_details(youtube_link, language_code)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Summarize AI says:")
        st.write(summary)
    else:
        st.write("No transcript available for the selected language.")
