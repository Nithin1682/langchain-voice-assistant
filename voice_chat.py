import time, re, pyperclip, speech_recognition as sr, pyttsx3
from chatbot_core import app, enrich_with_datetime, detect_intent, check_grammar, suggest_emoji
from langchain_core.messages import HumanMessage

# Setup
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170)
WAKE_WORD = 'hey google'
SILENCE_TIMEOUT = 4

# Emoji remover
def remove_emojis(text: str) -> str:
    pattern = re.compile('[\U0001F600-\U0001F64F' +
                         '\U0001F300-\U0001F5FF' +
                         '\U0001F680-\U0001F6FF' +
                         '\U0001F1E0-\U0001F1FF' +
                         '\u2600-\u26FF]+', flags=re.UNICODE)
    return pattern.sub('', text)

# TTS & STT helpers
def speak(text: str):
    tts_engine.say(text); tts_engine.runAndWait()

def listen(timeout=5, phrase_time_limit=10) -> str:
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=0.5)
        try:
            audio=recognizer.listen(mic, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return recognizer.recognize_google(audio).lower()
        except: return ''

# Main loop
def chat_with_voice(thread_id: str):
    enrich_with_datetime(thread_id)
    print(f"Say '{WAKE_WORD}' to start. 'exit' to quit.")
    cfg={'configurable':{'thread_id':thread_id}}

    while True:
        if WAKE_WORD in listen():
            speak('Yes?')
            last_time=time.time(); active=True
            while active:
                user_text=listen().strip()
                if not user_text and time.time()-last_time>SILENCE_TIMEOUT:
                    speak('Going back'); active=False; break
                if not user_text: continue
                print('You:',user_text)
                if user_text.lower()=='exit':
                    speak('Goodbye!'); return

                intent=detect_intent(user_text)
                # Grammar
                if intent=='check_grammar':
                    txt=pyperclip.paste().strip()
                    if txt:
                        corr=check_grammar(txt)
                        if corr!=txt: pyperclip.copy(corr); speak('Corrected and copied.')
                        else: speak('No mistakes found.')
                    else: speak('Clipboard empty.')
                    continue
                # Emoji
                if intent=='suggest_emoji':
                    txt=pyperclip.paste().strip()
                    if txt: pyperclip.copy(suggest_emoji(txt)); speak('Emoji copied.')
                    else: speak('Clipboard empty.')
                    continue

                # General chat
                last_time=time.time()
                out=app.invoke({'messages':[HumanMessage(content=user_text)]},cfg)
                reply=out['messages'][-1].content
                print('Assistant:',reply)
                speak(remove_emojis(reply))

if __name__=='__main__':
    chat_with_voice(input("Enter thread ID: "))