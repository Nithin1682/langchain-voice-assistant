Project Title: LangChain + Groq AI Assistant with Timetable, Grammar, and Emoji Support

🧠 Description:
This is an AI-powered personal assistant that uses LangChain + Groq APIs. It supports both text and voice input, and allows you to:

✅ Extract your weekly timetable from an image
🗑️ Delete existing timetable
✍️ Check grammar and spelling mistakes from copied text
😊 Suggest relevant emojis for a given sentence
🎤 Activate via voice with wake word: "hey google"

All features work via text CLI or voice control.

🗃️ Project Structure:
plaintext
Copy
Edit
├── chatbot_core.py       # Main text assistant using LangChain + Groq
├── voice_chat.py         # Voice assistant with microphone and TTS
├── timetable_tool.py     # Handles timetable extraction, saving, deletion
├── README.txt            # This file
└── timetable.json        # (Auto-created) Stores your timetable in JSON

🔧 Setup Instructions:
Clone your project folder or create a new directory and add all .py files.

Install required packages:

bash
pip install langchain groq openai pyttsx3 SpeechRecognition pyperclip pynput

Add your Groq API Key (you will be prompted at runtime):

No need to hardcode your key. The script asks for it when run.

▶️ Running the Assistant:
1. Text Mode (CLI):

bash
python chatbot_core.py

Enter your text commands like:

save my timetable
check grammar
suggest emoji
delete my timetable

2. Voice Mode:

bash
python voice_chat.py

Say “hey google” to activate. Speak naturally like:

“Check the grammar of copied text”
“Give me emoji for copied sentence”
“Save my timetable”
“Delete my timetable”

📋 Features Quick Summary:

Feature	Trigger (text or voice)	Action
Save Timetable	save my timetable	Upload image, auto-extract & save
Delete Timetable	delete my timetable	Clears saved JSON + LLM memory
Grammar Check	check grammar	Fix grammar in copied text & update clipboard
Emoji Suggestion	suggest emoji	Suggest emoji for copied text

💡 Notes:
Make sure you have microphone access for voice mode.
Timetable image parsing uses Groq’s llama-4-scout-17b vision model.
Extracted timetable is saved as timetable.json in the same folder.