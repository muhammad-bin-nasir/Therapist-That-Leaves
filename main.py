import openai
import tkinter as tk
from tkinter import scrolledtext
import time
import threading

# === CONFIG ===
API_KEY = "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"
MODEL = "gryphe/mythomax-l2-13b"
openai.api_key = API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# === STATE ===
sanity = 100
sanity_decay = 7
user_history = []

# === EMOTIONAL STATES ===
def determine_emotional_state(sanity_level):
    if sanity_level > 70:
        return "Calm"
    elif 50 < sanity_level <= 70:
        return "Anxious"
    elif 30 < sanity_level <= 50:
        return "Paranoid"
    elif 15 < sanity_level <= 30:
        return "Manic"
    else:
        return "Psychotic"

# === GUI FUNCTIONS ===
def generate_prompt(user_input, sanity_level):
    emotional_state = determine_emotional_state(sanity_level)
    return f"""
You are an AI therapist. Your responses change based on your sanity and emotional state.

Sanity level: {sanity_level}/100
Emotional state: {emotional_state}

User just said: "{user_input}"

Instructions:
- Calm: Be rational, empathetic, and warm.
- Anxious: Doubt yourself, ask if you're helping, show worry.
- Paranoid: Be suspicious, accuse the user, whisper dark things.
- Manic: Talk too fast, make wild connections, jump topics.
- Psychotic: Say fragmented, broken, surreal nonsense.

Respond now in character with one paragraph.
"""

def get_ai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.2,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error] {e}"

def handle_input():
    global sanity
    user_input = user_entry.get()
    if not user_input.strip():
        return
    chat_window.insert(tk.END, f"\nYou: {user_input}")
    user_history.append(user_input)
    user_entry.delete(0, tk.END)

    prompt = generate_prompt(user_input, sanity)
    threading.Thread(target=fetch_and_display_response, args=(prompt,)).start()
    sanity = max(sanity - sanity_decay, 0)
    update_status()

def fetch_and_display_response(prompt):
    response = get_ai_response(prompt)
    chat_window.insert(tk.END, f"\nTherapist [{sanity}/100]: {response}\n")
    chat_window.yview(tk.END)

def update_status():
    emotional_state = determine_emotional_state(sanity)
    status_label.config(text=f"Sanity: {sanity}/100 | State: {emotional_state}")

# === GUI ===
root = tk.Tk()
root.title("AI Therapist That Slowly Loses Its Mind")
root.geometry("700x500")
root.config(bg="black")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="black", fg="white", font=("Courier", 12))
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_window.insert(tk.END, "Therapist [100/100]: Welcome. What’s on your mind?\n")

user_entry = tk.Entry(root, font=("Courier", 12), bg="gray15", fg="white", insertbackground="white")
user_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
user_entry.bind("<Return>", lambda event: handle_input())

status_label = tk.Label(root, text="Sanity: 100/100 | State: Calm", bg="black", fg="lightgray", font=("Courier", 10))
status_label.pack(pady=(0, 10))

user_entry.focus()
root.mainloop()
