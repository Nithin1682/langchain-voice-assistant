import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import List, Tuple

DB_PATH = os.environ.get("TIMETABLE_DB", "timetable.db")

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
      CREATE TABLE IF NOT EXISTS timetable (
        day TEXT,
        period INTEGER,
        start TEXT,
        end TEXT,
        subject TEXT
      )
    """)
    conn.commit()
    conn.close()

def save_timetable_gui():
    _init_db()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    popup = tk.Tk()
    popup.title("How many periods per day?")
    tk.Label(popup, text="Number of periods:").grid(row=0, column=0)
    num_entry = tk.Entry(popup); num_entry.grid(row=0, column=1)

    def on_num():
        try:
            n = int(num_entry.get())
            popup.destroy()
            _build_grid(n, days)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid integer.")

    tk.Button(popup, text="OK", command=on_num).grid(row=1, column=1)
    popup.mainloop()
    return "Timetable saved to database."

def _build_grid(n_periods: int, days: List[str]):
    win = tk.Tk()
    win.title("Enter timetable")
    tk.Label(win, text="Period#").grid(row=0, column=0)
    tk.Label(win, text="Start (HH:MM)").grid(row=0, column=1)
    tk.Label(win, text="End   (HH:MM)").grid(row=0, column=2)
    for di, day in enumerate(days):
        tk.Label(win, text=day).grid(row=0, column=3+di)

    entries = {}
    for p in range(1, n_periods+1):
        tk.Label(win, text=str(p)).grid(row=p, column=0)
        s = tk.Entry(win); s.grid(row=p, column=1)
        e = tk.Entry(win); e.grid(row=p, column=2)
        for di, day in enumerate(days):
            subj = tk.Entry(win)
            subj.grid(row=p, column=3+di)
            entries[(day, p)] = (s, e, subj)

    def on_save():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM timetable")
        for (day, p), (s, e, subj) in entries.items():
            start, end, sub = s.get().strip(), e.get().strip(), subj.get().strip()
            if start and end and sub:
                c.execute(
                    "INSERT INTO timetable (day, period, start, end, subject) VALUES (?,?,?,?,?)",
                    (day, p, start, end, sub)
                )
        conn.commit()
        conn.close()
        win.destroy()
        #messagebox.showinfo("Saved", "Timetable saved!")

    tk.Button(win, text="Save", command=on_save).grid(row=n_periods+1, column=1)
    win.mainloop()

def get_timetable_markdown() -> str:
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT day, start, end, subject FROM timetable ORDER BY day, start")
    rows: List[Tuple[str, str, str, str]] = c.fetchall()
    conn.close()

    if not rows:
        return "The timetable is currently empty."

    md_lines = [
        "| Day      | Start (24hr) | End (24hr) | Subject |",
        "|----------|--------------|------------|---------|"
    ]
    for day, start, end, subj in rows:
        md_lines.append(f"| {day:<8} | {start:<12} | {end:<10} | {subj:<15} |")
    return "\n".join(md_lines)

def delete_timetable() -> str:
    """
    Deletes all timetable entries from the database.
    """
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM timetable")
    conn.commit()
    conn.close()
    return "Your timetable has been deleted."
