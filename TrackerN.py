import tkinter as tk
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json

class MultiDiceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Dice Roll Tracker")
        self.num_dice = tk.IntVar(value=1)
        self.rolls = []
        self.current_roll = []
        self.faces = [1, 2, 3, 4, 5, 6]
        self.roll_file = None
        self.canvas = None
        self.button_vars = {}
        self.percent_vars = {}
        self.total_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Set number of dice and start rolling!")
        
        # Load preferences
        self.dark_mode = self.load_preference("dark_mode", False)
        
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        tk.Label(top_frame, text="Number of dice:", font=("Arial", 12)).pack(side=tk.LEFT)
        dice_entry = tk.Entry(top_frame, textvariable=self.num_dice, width=3, font=("Arial", 12))
        dice_entry.pack(side=tk.LEFT, padx=5)
        set_btn = tk.Button(top_frame, text="Set", command=self.set_dice, font=("Arial", 12))
        set_btn.pack(side=tk.LEFT)
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 12))
        self.status_label.pack(pady=(0,5))
        self.graph_frame = tk.Frame(self.root)
        self.graph_frame.pack(pady=(5, 0))
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=10)
        self.reset_btn = tk.Button(self.root, text="Reset", width=8, height=2, font=("Arial", 12), command=self.reset_rolls, bg='red', fg='white')
        self.reset_btn.pack(pady=(10,0))
        self.total_label = tk.Label(self.root, textvariable=self.total_var, font=("Arial", 12, "bold"))
        self.total_label.pack(pady=(5,0))
        self.set_dice()

    def set_dice(self):
        try:
            n = int(self.num_dice.get())
            if n < 1 or n > 20:
                raise ValueError
        except ValueError:
            self.status_var.set("Enter a valid number of dice (1-20)")
            return
            
        self.roll_file = f"dice_rolls_{n}.dicegraph"
        self.rolls = self.read_rolls()
        self.current_roll = []
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.button_vars = {}
        self.percent_vars = {}
        for j, val in enumerate(self.faces):
            btn = tk.Button(self.frame, text=str(val), width=6, height=2, font=("Arial", 16),
                            command=lambda v=val: self.on_roll(v))
            btn.grid(row=0, column=j, padx=5)
            var = tk.StringVar(value="0")
            tk.Label(self.frame, textvariable=var, font=("Arial", 12)).grid(row=1, column=j)
            self.button_vars[val] = var
            percent_var = tk.StringVar(value="0.0%")
            tk.Label(self.frame, textvariable=percent_var, font=("Arial", 10)).grid(row=2, column=j)
            self.percent_vars[val] = percent_var
        self.update_button_counts()
        self.show_graph()
        self.status_var.set(f"Ready to roll {n} dice. Click {n} values for each entry.")

    def on_roll(self, value):
        n = self.num_dice.get()
        self.current_roll.append(value)
        if len(self.current_roll) < n:
            self.status_var.set(f"Selected: {','.join(map(str, self.current_roll))} (click {n-len(self.current_roll)} more)")
        else:
            self.log_roll(self.current_roll)
            self.status_var.set(f"Rolled: {','.join(map(str, self.current_roll))}")
            self.current_roll = []
            self.rolls = self.read_rolls()
            self.update_button_counts()
            self.show_graph()

    def log_roll(self, values):
        with open(self.roll_file, 'a') as f:
            f.write(','.join(map(str, values)) + '\n')

    def read_rolls(self):
        if not os.path.exists(self.roll_file):
            return []
        with open(self.roll_file, 'r') as f:
            lines = f.readlines()
        rolls = [list(map(int, line.strip().split(','))) for line in lines if line.strip()]
        return rolls

    def reset_rolls(self):
        with open(self.roll_file, 'w') as f:
            pass
        self.rolls = []
        self.current_roll = []
        self.update_button_counts()
        self.show_graph()
        self.status_var.set("Rolls reset!")

    def update_button_counts(self):
        n = self.num_dice.get()
        counts = Counter([v for roll in self.rolls if len(roll) == n for v in roll])
        total = len([roll for roll in self.rolls if len(roll) == n]) * n if n > 0 else 0
        self.total_var.set(f"Total Rolls: {total//n if n else 0}")
        for val in self.faces:
            count = counts[val]
            self.button_vars[val].set(str(count))
            percent = (count / total * 100) if total > 0 else 0.0
            self.percent_vars[val].set(f"{percent:.1f}%")

    def show_graph(self):
        n = self.num_dice.get()
        counts = Counter([v for roll in self.rolls if len(roll) == n for v in roll])
        
        # Create figure with dark mode support
        fig = plt.Figure(figsize=(6, 3), dpi=100)
        fig.clf()
        
        # Apply dark mode if enabled
        if self.dark_mode:
            plt.style.use('dark_background')
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
        
        vals = [counts[face] for face in self.faces]
        bars = ax.bar([str(f) for f in self.faces], vals, color=bar_color)
        
        # Set text colors for dark mode compatibility
        ax.set_title(f'Dice Value Distribution (all dice)', color=text_color)
        ax.set_xlabel('Dice Value', color=text_color)
        ax.set_ylabel('Count', color=text_color)
        ax.tick_params(colors=text_color)
        
        for spine in ax.spines.values():
            spine.set_color(text_color)
            
        fig.tight_layout()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
    def load_preference(self, key, default):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiDiceTracker(root)
    root.mainloop()
