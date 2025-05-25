import tkinter as tk
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# File to store dice rolls
ROLLS_FILE = 'dice_rolls.txt'

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
    fig = plt.Figure(figsize=(6, 3), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar([str(f) for f in faces], values, color='skyblue')
    ax.set_xlabel('Dice Value')
    ax.set_ylabel('Count')
    ax.set_title('Dice Roll Counts')
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

def reset_rolls():
    with open(ROLLS_FILE, 'w') as f:
        pass
    status_var.set("Rolls reset!")
    show_graph()

status_var = tk.StringVar()
status_var.set("Ready")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

button_vars = {}
percent_vars = {}
total_var = tk.StringVar()
total_var.set("")

for val in [1, 2, 3, 4, 5, 6]:
    btn = tk.Button(frame, text=str(val), width=6, height=2, font=("Arial", 16),
                    command=lambda v=val: on_roll(v))
    btn.grid(row=0, column=val-1, padx=5)
    var = tk.StringVar()
    var.set("0")
    label = tk.Label(frame, textvariable=var, font=("Arial", 12))
    label.grid(row=1, column=val-1)
    button_vars[val] = var
    percent_var = tk.StringVar()
    percent_var.set("0.0%")
    percent_label = tk.Label(frame, textvariable=percent_var, font=("Arial", 10))
    percent_label.grid(row=2, column=val-1)
    percent_vars[val] = percent_var

total_label = tk.Label(frame, textvariable=total_var, font=("Arial", 12, "bold"))
total_label.grid(row=3, column=0, columnspan=6, pady=(5,0))

def update_button_counts():
    rolls = read_rolls()
    counts = Counter(rolls)
    total = len(rolls)
    total_var.set(f"Total Rolls: {total}")
    for val in [1, 2, 3, 4, 5, 6]:
        count = counts.get(val, 0)
        button_vars[val].set(str(count))
        percent = (count / total * 100) if total > 0 else 0.0
        percent_vars[val].set(f"{percent:.1f}%")

reset_btn = tk.Button(root, text="Reset", width=8, height=2, font=("Arial", 12), command=reset_rolls, bg='red', fg='black')
reset_btn.pack(pady=(10,0))

status_label = tk.Label(root, textvariable=status_var, font=("Arial", 12))
status_label.pack(pady=(10,0))

# Call show_graph once at startup to show initial graph
show_graph()

root.mainloop()