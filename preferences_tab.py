"""
Preferences tab implementation for the DiceGraph application.
Handles user preference settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

import user_preferences as prefs
from file_utils import (
    reset_file, delete_file, get_available_dice_sets, 
    SINGLE_DICE_DIR, MULTIPLE_DICE_DIR, SIMULATION_DIR, FILE_EXTENSION
)
import sv_ttk

class PreferencesTab:
    """Class to manage the preferences tab in the application"""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the preferences tab.
        
        Args:
            parent: The parent frame
            app_instance: The main application instance
        """
        self.parent = parent
        self.app = app_instance
        
        # Load existing preferences
        self.preferences = prefs.load_preferences()
        
        # Initialize UI variables
        self.pref_default_faces = tk.IntVar(value=self.preferences.get('default_faces', 6))
        self.pref_dark_mode = tk.BooleanVar(value=self.preferences.get('dark_mode', False))
        self.pref_alpha = tk.DoubleVar(value=self.preferences.get('statistical_alpha', 0.05))
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preferences tab UI"""
        # General preferences section
        general_frame = ttk.LabelFrame(self.parent, text="General Preferences")
        general_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Default number of faces
        pf_frame = ttk.Frame(general_frame)
        pf_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pf_frame, text="Default number of faces:").pack(side=tk.LEFT, padx=5)
        default_faces_spin = ttk.Spinbox(
            pf_frame, from_=2, to=100, width=5, 
            textvariable=self.pref_default_faces, 
            command=self.on_pref_faces_change
        )
        default_faces_spin.pack(side=tk.LEFT, padx=5)
        
        # Dark mode toggle
        dm_frame = ttk.Frame(general_frame)
        dm_frame.pack(fill=tk.X, pady=5)
        ttk.Checkbutton(
            dm_frame, text="Dark Mode", variable=self.pref_dark_mode, 
            command=self.on_pref_dark_mode_toggle
        ).pack(side=tk.LEFT, padx=5)
        
        # Statistical settings section
        stats_frame = ttk.LabelFrame(self.parent, text="Statistical Settings")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Alpha level for significance tests
        alpha_frame = ttk.Frame(stats_frame)
        alpha_frame.pack(fill=tk.X, pady=5)
        ttk.Label(alpha_frame, text="Statistical significance level (α):").pack(side=tk.LEFT, padx=5)
        
        # Create custom alpha values
        alpha_values = ["0.01", "0.05", "0.10"]
        alpha_combobox = ttk.Combobox(
            alpha_frame, width=5, textvariable=self.pref_alpha,
            values=alpha_values
        )
        alpha_combobox.pack(side=tk.LEFT, padx=5)
        alpha_combobox.bind("<<ComboboxSelected>>", self.on_pref_alpha_change)
        
        # Data management section
        data_frame = ttk.LabelFrame(self.parent, text="Data Management")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear data buttons
        clear_frame = ttk.Frame(data_frame)
        clear_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            clear_frame, text="Clear Single Dice Data", 
            command=lambda: self.clear_data_directory(SINGLE_DICE_DIR, "single die")
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            clear_frame, text="Clear Multiple Dice Data", 
            command=lambda: self.clear_data_directory(MULTIPLE_DICE_DIR, "multiple dice")
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(
            clear_frame, text="Clear Simulations", 
            command=lambda: self.clear_data_directory(SIMULATION_DIR, "simulations")
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Clear all data button
        ttk.Button(
            data_frame, text="Clear All Data", 
            command=self.clear_all_data, 
            style='Accent.TButton'
        ).pack(pady=10)
    
    def on_pref_faces_change(self):
        """Update default faces in roller and simulator"""
        value = self.pref_default_faces.get()
        # Update preference
        self.preferences['default_faces'] = value
        prefs.save_preferences(self.preferences)
        
        # Update main app
        self.app.dice_faces.set(value)
        
        # Also update simulator if it exists
        if hasattr(self.app, 'simulator_tab') and self.app.simulator_tab:
            self.app.simulator_tab.sim_faces.set(value)
    
    def on_pref_dark_mode_toggle(self):
        """Toggle dark mode theme"""
        dark_mode = self.pref_dark_mode.get()
        # Update preference
        self.preferences['dark_mode'] = dark_mode
        prefs.save_preferences(self.preferences)
        
        # Update theme
        sv_ttk.set_theme("dark" if dark_mode else "light")
        
        # Refresh graphs if they exist
        if hasattr(self.app, 'roller_tab') and self.app.roller_tab:
            self.app.roller_tab.show_graph()
        
        if hasattr(self.app, 'simulator_tab') and self.app.simulator_tab and self.app.simulator_tab.last_simulation:
            faces = self.app.simulator_tab.sim_faces.get()
            self.app.simulator_tab.show_simulation_results(
                self.app.simulator_tab.last_simulation, faces
            )
    
    def on_pref_alpha_change(self, event=None):
        """Update alpha level for statistical tests"""
        value = self.pref_alpha.get()
        # Update preference
        self.preferences['statistical_alpha'] = value
        prefs.save_preferences(self.preferences)
        
        # If simulator has results, refresh to reflect new alpha
        if hasattr(self.app, 'simulator_tab') and self.app.simulator_tab and self.app.simulator_tab.last_simulation:
            faces = self.app.simulator_tab.sim_faces.get()
            self.app.simulator_tab.show_simulation_results(
                self.app.simulator_tab.last_simulation, faces
            )
    
    def clear_data_directory(self, directory, description):
        """Clear all data files in a directory"""
        if messagebox.askyesno("Confirm Clear", 
                             f"Are you sure you want to clear all {description} data? This cannot be undone."):
            # Get all files in directory
            if os.path.exists(directory):
                files = [f for f in os.listdir(directory) if f.endswith(f'.{FILE_EXTENSION}')]
                for file in files:
                    file_path = os.path.join(directory, file)
                    delete_file(file_path)
                messagebox.showinfo("Data Cleared", f"All {description} data has been cleared.")
            
            # Refresh graphs if needed
            if hasattr(self.app, 'roller_tab') and self.app.roller_tab:
                self.app.roller_tab.show_graph()
            
            if hasattr(self.app, 'simulator_tab') and self.app.simulator_tab:
                for widget in self.app.simulator_tab.sim_graph_container.winfo_children():
                    widget.destroy()
                self.app.simulator_tab.last_simulation = None
    
    def clear_all_data(self):
        """Clear all saved dice data"""
        if messagebox.askyesno("Confirm Clear", 
                             "Are you sure you want to clear ALL dice data? This cannot be undone."):
            # Reset each file in all directories
            for directory in [SINGLE_DICE_DIR, MULTIPLE_DICE_DIR, SIMULATION_DIR]:
                if os.path.exists(directory):
                    files = [f for f in os.listdir(directory) if f.endswith(f'.{FILE_EXTENSION}')]
                    for file in files:
                        file_path = os.path.join(directory, file)
                        delete_file(file_path)
            
            messagebox.showinfo("Data Cleared", "All dice data has been cleared.")
            
            # Refresh graphs
            if hasattr(self.app, 'roller_tab') and self.app.roller_tab:
                self.app.roller_tab.show_graph()
            
            if hasattr(self.app, 'simulator_tab') and self.app.simulator_tab:
                for widget in self.app.simulator_tab.sim_graph_container.winfo_children():
                    widget.destroy()
                self.app.simulator_tab.last_simulation = None
