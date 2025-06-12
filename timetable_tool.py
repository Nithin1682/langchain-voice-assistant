# timetable_tool.py
import os
import json
import base64
import tkinter as tk
from tkinter import filedialog
from groq import Groq

# Path for your saved JSON timetable
JSON_PATH = os.environ.get("TIMETABLE_JSON", "timetable.json")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


def _exists() -> bool:
    return os.path.isfile(JSON_PATH)


def _transform_table_schema(raw: list) -> list:
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    transformed = []
    for idx, row in enumerate(raw):
        time_str = row.get('time', '')
        parts = time_str.split('-')
        start = parts[0].strip() if parts else ''
        end = parts[1].strip() if len(parts) > 1 else ''
        period = idx + 1
        for day in days:
            subj = row.get(day, '').strip()
            if subj:
                transformed.append({
                    'day': day.capitalize(),
                    'period': period,
                    'start': start,
                    'end': end,
                    'subject': subj
                })
    return transformed


def save_timetable_image() -> str:
    if _exists():
        return "There is a timetable already saved."

    # 1. File-picker
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Upload timetable image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
    )
    if not file_path:
        return "No image selected — timetable not saved."

    # 2. Read & base64-encode
    with open(file_path, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    # 3. MIME type
    ext = file_path.rsplit('.', 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    # 4. Send to Groq LLaMA-4 Scout
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the timetable from this image in structured JSON format. Return ONLY the JSON array."},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}}
            ],
        }],
        temperature=0.0,
        max_completion_tokens=1024
    )

    # 5. Clean up fences + parse
    raw_content = response.choices[0].message.content.strip()
    if raw_content.startswith("```"):
        lines = raw_content.splitlines()
        if lines[-1].startswith("```"):
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        json_str = "\n".join(lines)
    else:
        json_str = raw_content

    try:
        raw = json.loads(json_str)
        if isinstance(raw, list) and raw and isinstance(raw[0], dict) and 'time' in raw[0]:
            data = _transform_table_schema(raw)
        else:
            data = raw

        with open(JSON_PATH, "w", encoding="utf-8") as jf:
            json.dump(data, jf, indent=2)
        return "✅ Timetable extracted and saved to JSON."

    except json.JSONDecodeError:
        return f"❌ Failed to parse JSON. Cleaned content was:\n\n{json_str}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


def load_timetable_json(raw: bool = False) -> str:
    if not _exists():
        return "[]" if raw else "The timetable is currently empty."

    with open(JSON_PATH, "r", encoding="utf-8") as jf:
        data = json.load(jf)

    if raw:
        return json.dumps(data, indent=2)

    # build markdown
    lines = ["| Day     | Period | Start  | End    | Subject            |",
             "|---------|--------|--------|--------|--------------------|"]
    for entry in data:
        lines.append(
            f"| {entry['day']:<7} | {entry['period']:<6} | {entry['start']:<6} | {entry['end']:<6} | {entry['subject']:<18} |"
        )
    return "\n".join(lines)


def delete_timetable() -> str:
    if _exists():
        os.remove(JSON_PATH)
        return "Your timetable has been deleted."
    return "No timetable was saved."