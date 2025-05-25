"""
Main GUI implementation for the DiceGraph application.
"""

import tkinter as tk
from tkinter import ttk

from dice_manager import DiceManager
from file_utils import ensure_directories
import user_preferences as prefs
import sv_ttk

from dice_roller import DiceRollerTab
from dice_simulator import DiceSimulatorTab
from preferences_tab import PreferencesTab

class DiceTrackerApp:
    """Main application class for Dice Tracker"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Dice Roll Tracker")
        
        # Load preferences
        preferences = prefs.load_preferences()
        
        # Set window size from preferences
        window_width = preferences.get('window_width', 800)
        window_height = preferences.get('window_height', 600)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Set theme from preferences
        dark_mode = preferences.get('dark_mode', False)
        sv_ttk.set_theme("dark" if dark_mode else "light")
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize dice manager
        self.dice_manager = DiceManager()
        
        # UI variables
        self.num_dice = tk.IntVar(value=1)
        self.dice_faces = tk.IntVar(value=preferences.get('default_faces', 6))
        self.dice_name = tk.StringVar(value="Default")
        self.status_var = tk.StringVar(value="Ready to roll!")
        self.total_var = tk.StringVar(value="")
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Main notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab frames
        roller_frame = ttk.Frame(notebook)
        simulator_frame = ttk.Frame(notebook)
        preferences_frame = ttk.Frame(notebook)
        
        notebook.add(roller_frame, text="Dice Roller")
        notebook.add(simulator_frame, text="Dice Simulator")
        notebook.add(preferences_frame, text="Preferences")
        
        # Create the tab instances
        self.roller_tab = DiceRollerTab(roller_frame, self)
        self.simulator_tab = DiceSimulatorTab(simulator_frame, self)
        self.preferences_tab = PreferencesTab(preferences_frame, self)
        
    def save_window_size(self):
        """Save the current window size to preferences"""
        preferences = prefs.load_preferences()
        preferences['window_width'] = self.root.winfo_width()
        preferences['window_height'] = self.root.winfo_height()
        prefs.save_preferences(preferences)