import tkinter as tk
from tkinter import ttk
import sv_ttk  # Sun Valley TTK theme
import os

from gui import DiceTrackerApp
from file_utils import ensure_directories, SINGLE_DICE_DIR, MULTIPLE_DICE_DIR, SIMULATION_DIR

def setup_styles():
    """Setup ttk styles"""
    style = ttk.Style()
    style.configure('Accent.TButton', foreground='white', background='red')

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    sv_ttk.set_theme("dark")  # Set default theme to light using Sun Valley theme
    root.title("Dice Tracker")
    root.minsize(800, 600)
    
    # Setup styles
    setup_styles()
      # Create app
    app = DiceTrackerApp(root)
    app.setup_ui()
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
