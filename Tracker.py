import tkinter as tk
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json

# File to store dice rolls
ROLLS_FILE = 'dice_rolls.dicegraph'

def log_roll(value):
    with open(ROLLS_FILE, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {value}\n")

def read_rolls():
    try:
        with open(ROLLS_FILE, 'r') as f:
            lines = f.readlines()
        rolls = [int(line.strip().split('-')[-1]) for line in lines if line.strip() and line.strip().split('-')[-1].strip().isdigit()]
        return rolls
    except FileNotFoundError:
        return []

# Load user preferences
def load_preference(key, default):
    """Load a preference from the preferences file"""
    prefs_file = "usersettings.dicegraphprefs"
    try:
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                prefs = json.load(f)
            return prefs.get(key, default)
    except:
        pass
    return default

# Dark mode setting
DARK_MODE = load_preference("dark_mode", False)

root = tk.Tk()
root.title("Dice Roll Tracker")

graph_frame = tk.Frame(root)
graph_frame.pack(pady=(10, 0))

canvas = None

def show_graph():
    global canvas
    rolls = read_rolls()
    counts = Counter(rolls)
    faces = [1, 2, 3, 4, 5, 6]
    values = [counts.get(face, 0) for face in faces]
    
    # Create figure with dark mode support
    fig = plt.Figure(figsize=(6, 3), dpi=100)
    
    # Apply dark mode if enabled
    if DARK_MODE:
        bg_color = '#303030'
        text_color = 'white'
        bar_color = '#5599ff'
    else:
        bg_color = 'white'
        text_color = 'black'
        bar_color = 'skyblue'
        
    fig.patch.set_facecolor(bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)
    
    bars = ax.bar([str(f) for f in faces], values, color=bar_color)
    
    # Set text colors for dark mode compatibility
    ax.set_title('Dice Roll Counts', color=text_color)
    ax.set_xlabel('Dice Value', color=text_color)
    ax.set_ylabel('Count', color=text_color)
    ax.tick_params(colors=text_color)
    
    for spine in ax.spines.values():
        spine.set_color(text_color)
        
    fig.tight_layout()
    
    if canvas:
        canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    update_button_counts()

def on_roll(value):
    log_roll(value)
    status_var.set(f"Rolled: {value}")
    show_graph()

frame = tk.Frame(root)
frame.pack(padx=20, pady=10)

button_vars = {}
percent_vars = {}
total_var = tk.StringVar()
status_var = tk.StringVar(value="Ready to roll!")

faces = [1, 2, 3, 4, 5, 6]
for i, val in enumerate(faces):
    btn = tk.Button(frame, text=str(val), width=6, height=2, font=("Arial", 16), 
                    command=lambda v=val: on_roll(v))
    btn.grid(row=0, column=i, padx=5)
    var = tk.StringVar(value="0")
    tk.Label(frame, textvariable=var, font=("Arial", 12)).grid(row=1, column=i)
    button_vars[val] = var
    percent_var = tk.StringVar(value="0.0%")
    tk.Label(frame, textvariable=percent_var, font=("Arial", 10)).grid(row=2, column=i)
    percent_vars[val] = percent_var

def update_button_counts():
    rolls = read_rolls()
    counts = Counter(rolls)
    total = len(rolls)
    total_var.set(f"Total Rolls: {total}")
    for val in faces:
        count = counts.get(val, 0)
        button_vars[val].set(str(count))
        percent = (count / total * 100) if total > 0 else 0.0
        percent_vars[val].set(f"{percent:.1f}%")

def reset_rolls():
    with open(ROLLS_FILE, 'w') as f:
        pass
    status_var.set("Rolls reset!")
    show_graph()

reset_button = tk.Button(root, text="Reset", width=8, height=2, font=("Arial", 12), 
                        command=reset_rolls, bg='red', fg='white')
reset_button.pack(pady=(10,0))

status_label = tk.Label(root, textvariable=status_var, font=("Arial", 12))
status_label.pack(pady=(5,0))

total_label = tk.Label(root, textvariable=total_var, font=("Arial", 12, "bold"))
total_label.pack(pady=(5,0))

# Show initial graph
show_graph()

root.mainloop()
