# 🧠 LangChain Voice Assistant (Groq + Clipboard Tools)

This is a smart desktop assistant built with **LangChain**, **Groq**, and Python. It supports **text and voice interaction**, clipboard tools like **grammar correction** and **emoji suggestion**, and allows **timetable management** using a GUI.

---

## 🚀 How to Run

### 🖥️ Text Mode (Terminal)

bash
python chatbot_core.py

🎙️ Voice Mode (Mic + Speaker Required)

bash
python voice_chat.py

✨ Features
✅ Clipboard Grammar Correction
✅ Emoji Suggestion for Copied Text
✅ Save/Delete Weekly Timetable using GUI (Tkinter)
✅ Memory-based LangChain conversation
✅ Wake word detection: “Hey Google”
✅ Voice interaction using microphone and speaker
✅ Local SQLite database (timetable.db)

📋 Clipboard Use Cases
Grammar Check:

Copy a sentence → say "check the context for any grammatical mistakes"
If incorrect, it will copy the corrected sentence back

Emoji Suggestion:

Copy a sentence → say "give me an emoji for this sentence"
It will copy one or two emojis based on the context

🛠️ Setup Instructions
1. Clone the Repository

bash
git clone https://github.com/yourusername/LLM.git
cd LLM

2. Create Virtual Environment

bash
python -m venv langgraph-env
source langgraph-env/bin/activate   # On Windows: langgraph-env\Scripts\activate

3. Install Requirements

bash
pip install -r requirements.txt

4. Run the Assistant

bash
python chatbot_core.py      # For text mode
python voice_chat.py        # For voice assistant

🧩 Files & Structure
bash
Copy
Edit
LLM/
├── chatbot_core.py        # Core logic (LLM, tools, intent detection)
├── voice_chat.py          # Voice assistant with wake word + clipboard tools
├── timetable_tool.py      # GUI + DB for managing class timetable
├── requirements.txt       # Dependencies
├── .gitignore             # Git ignored files
├── README.md              # Project documentation
├── timetable.db           # SQLite DB (auto-created when needed)
└── langgraph-env/         # Your Python virtual environment (excluded from Git)

🔐 API Key Note
You’ll be prompted for your Groq API key when the assistant starts.
This keeps your key safe and not hardcoded in the script.

📦 Dependencies
Installable via requirements.txt

📌 Additional Info
Timetable GUI: Opens when you say "save timetable" or "delete timetable"
All timings use 24-hour format
No external cloud storage or servers required – runs completely on your machine

