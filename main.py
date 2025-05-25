import tkinter as tk
from tkinter import ttk

from gui import DiceTrackerApp

def setup_styles():
    """Setup ttk styles"""
    style = ttk.Style()
    style.configure('Accent.TButton', foreground='white', background='red')

def main():
    """Main entry point for the application"""
    root = tk.Tk()
    root.title("Dice Tracker")
    root.minsize(800, 600)
    
    # Setup styles
    setup_styles()
    
    # Create app
    app = DiceTrackerApp(root)
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
