# Groq Speech-to-Text Translation Demo

This Streamlit application demonstrates how to:
1. Record real-time audio input from users using Streamlit's `audio_input` feature
2. Process the audio using Groq's Speech-to-Text API
3. Translate the transcribed text to Chinese

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Features
- Real-time audio recording
- Speech-to-text transcription
- Translation to Chinese
- Display of both original transcription and translation

## Requirements
- Python 3.8+
- Streamlit 1.32.0+
- Groq API key
