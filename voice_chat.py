import speech_recognition as sr
import pyttsx3
import time
import pyperclip
import re

from chatbot_core import app, enrich_with_datetime, detect_intent, model
from langchain_core.messages import HumanMessage
from chatbot_core import check_grammar,suggest_emoji  # ensure you have this function in chatbot_core

recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)

WAKE_WORD = "hey google"
SILENCE_TIMEOUT = 10

def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002700-\U000027BF"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def speak(text: str):
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen(timeout=5, phrase_time_limit=10) -> str:
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.5)
        try:
            audio = recognizer.listen(mic, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return recognizer.recognize_google(audio).lower()
        except:
            return ""

def chat_with_voice(thread_id: str):
    enrich_with_datetime(thread_id)
    print(f"🌐 Say '{WAKE_WORD}' to start. 'exit' to quit.\n")
    cfg = {"configurable": {"thread_id": thread_id}}

    while True:
        transcript = listen(timeout=5, phrase_time_limit=5)
        if WAKE_WORD in transcript:
            speak("Yes, how can I help?")
            active = True
            last_time = time.time()
            while active:
                user_text = listen(timeout=5, phrase_time_limit=10).strip()
                if user_text:
                    print(f"You: {user_text}")
                    if user_text.lower() == "exit":
                        speak("Goodbye!")
                        return

                    # Detect intent using LLM
                    intent = detect_intent(user_text)

                    if intent == "check_grammar":
                        clipboard_text = pyperclip.paste().strip()
                        if clipboard_text:
                            corrected = check_grammar(clipboard_text)
                            if corrected.strip() != clipboard_text.strip():
                                pyperclip.copy(corrected)
                                speak("I found some mistakes. I've corrected and copied it back.")
                                print(f"Corrected: {corrected}")
                            else:
                                speak("No grammatical mistakes in the context.")
                        else:
                            speak("Clipboard is empty. Please copy the sentence first.")
                        continue  # skip fallback LLM
                    elif intent == "suggest_emoji":
                        clipboard_text = pyperclip.paste().strip()
                        if clipboard_text:
                            emoji = suggest_emoji(clipboard_text)
                            pyperclip.copy(emoji)
                            speak("Here's a suitable emoji suggestion. It's copied to your clipboard.")
                            print(f"Suggested Emoji: {emoji}")
                        else:
                            speak("Clipboard is empty. Please copy the sentence first.")
                        continue

                    last_time = time.time()
                    human_msg = HumanMessage(content=user_text)
                    out = app.invoke({"messages": [human_msg]}, cfg)
                    reply = out["messages"][-1].content
                    clean_reply = remove_emojis(reply)
                    print(f"Assistant: {reply}\n")
                    speak(clean_reply)

                elif time.time() - last_time > SILENCE_TIMEOUT:
                    speak("Going back to sleep.")
                    active = False

if __name__ == "__main__":
    session = input("Thread ID (e.g. 'default'): ")
    chat_with_voice(session)
