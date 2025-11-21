"""
voice_assistant.py
------------------
Handles voice input → transcription → RAG response → optional TTS playback.

Dependencies:
    pip install sounddevice wavio openai-whisper pyttsx3
"""

import sounddevice as sd
import wavio
import whisper
import pyttsx3
from src.rag.chain import answer_question


def record_audio(filename="query.wav", duration=5, samplerate=16000):
    """Record voice input from microphone."""
    print(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, samplerate, sampwidth=2)
    print("✅ Recording saved as", filename)
    return filename


def transcribe_audio(filename):
    """Transcribe speech to text using Whisper."""
    print("🧠 Transcribing audio...")
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    text = result["text"].strip()
    print("🗣️ Transcribed text:", text)
    return text


def get_ai_response(query):
    """Use RAG chain to answer the user's transcribed question."""
    print("🤖 Generating response...")
    answer = answer_question(query)
    print("💬 AI Response:", answer)
    return answer


def speak_text(text):
    """Convert text to speech (TTS)."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 175)
    engine.say(text)
    engine.runAndWait()


def run_voice_assistant():
    """Full pipeline: record → transcribe → query RAG → speak response."""
    filename = record_audio()
    query = transcribe_audio(filename)
    response = get_ai_response(query)
    speak_text(response)


if __name__ == "__main__":
    run_voice_assistant()
