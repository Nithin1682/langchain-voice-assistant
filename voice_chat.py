# voice_chat.py (unchanged)
import speech_recognition as sr
import pyttsx3
import time
import pyperclip
import re

from chatbot_core import app, enrich_with_datetime, detect_intent, check_grammar, suggest_emoji
from langchain_core.messages import HumanMessage

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
    return emoji_pattern.sub("", text)

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
            last_time = time.time()
            active = True
            while active:
                user_text = listen(timeout=5, phrase_time_limit=10).strip()
                if not user_text:
                    if time.time() - last_time > SILENCE_TIMEOUT:
                        speak("Going back to sleep.")
                        active = False
                    continue

                print(f"You: {user_text}")
                if user_text.lower() == "exit":
                    speak("Goodbye!")
                    return

                intent = detect_intent(user_text)
                if intent == "check_grammar":
                    txt = pyperclip.paste().strip()
                    if txt:
                        corr = check_grammar(txt)
                        if corr != txt:
                            pyperclip.copy(corr)
                            speak("Corrected and copied.")
                            print(f"Corrected: {corr}")
                        else:
                            speak("No mistakes found.")
                    else:
                        speak("Clipboard is empty.")
                    continue

                if intent == "suggest_emoji":
                    txt = pyperclip.paste().strip()
                    if txt:
                        emo = suggest_emoji(txt)
                        pyperclip.copy(emo)
                        speak("Emoji suggestion copied.")
                        print(f"Emoji: {emo}")
                    else:
                        speak("Clipboard is empty.")
                    continue

                last_time = time.time()
                out = app.invoke({"messages": [HumanMessage(content=user_text)]}, cfg)
                reply = out["messages"][-1].content
                print(f"Assistant: {reply}\n")
                speak(remove_emojis(reply))

if __name__ == "__main__":
    session = input("Thread ID (e.g. 'default'): ")
    chat_with_voice(session)