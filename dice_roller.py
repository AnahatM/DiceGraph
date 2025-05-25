"""
Dice roller implementation for the DiceGraph application.
Handles the dice rolling tab functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import os

from dice_manager import DiceManager
from file_utils import (
    get_file_path, log_single_roll, log_multiple_rolls,
    read_single_rolls, read_multiple_rolls, reset_file, delete_file,
    get_available_dice_sets, SINGLE_DICE_DIR, MULTIPLE_DICE_DIR
)
import user_preferences as prefs
from ui_components import SetSelectionDialog, StatsDialog
from statistics_utils import get_dice_fairness

class DiceRollerTab:
    """Class to manage the dice roller tab in the application"""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the dice roller tab.
        
        Args:
            parent: The parent frame
            app_instance: The main application instance
        """
        self.parent = parent
        self.app = app_instance
        self.dice_manager = app_instance.dice_manager
        
        # UI variables
        self.num_dice = app_instance.num_dice
        self.dice_faces = app_instance.dice_faces
        self.dice_name = app_instance.dice_name
        self.status_var = app_instance.status_var
        self.total_var = app_instance.total_var
        
        # UI components
        self.canvas = None
        self.button_vars = {}
        self.percent_vars = {}
        self.dice_buttons = []
        
        # Track fairness statistics
        self.last_fairness_stats = None
        
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the roller tab UI"""
        # Top frame for configuration
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Dice configuration
        config_frame = ttk.LabelFrame(top_frame, text="Dice Configuration")
        config_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Number of dice
        dice_frame = ttk.Frame(config_frame)
        dice_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dice_frame, text="Number of dice:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(dice_frame, from_=1, to=20, width=5, 
                    textvariable=self.num_dice).pack(side=tk.LEFT, padx=5)
        
        # Number of faces
        faces_frame = ttk.Frame(config_frame)
        faces_frame.pack(fill=tk.X, pady=5)
        ttk.Label(faces_frame, text="Number of faces:").pack(side=tk.LEFT, padx=5)
        self.faces_spin = ttk.Spinbox(faces_frame, from_=2, to=100, width=5, 
                                      textvariable=self.dice_faces)
        self.faces_spin.pack(side=tk.LEFT, padx=5)
        self.faces_spin.set(str(prefs.get_preference('default_faces', 6)))
        
        # Dice name
        name_frame = ttk.Frame(config_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Dice Set Name:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(name_frame, textvariable=self.dice_name, width=20).pack(side=tk.LEFT, padx=5)
        
        # Load/Apply buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Apply", command=self.apply_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Set", command=self.load_dice_set).pack(side=tk.LEFT, padx=5)
        
        # Status and data management section
        status_frame = ttk.LabelFrame(top_frame, text="Data Management")
        status_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Status label
        ttk.Label(status_frame, textvariable=self.status_var).pack(pady=5)
        
        # Data management buttons
        data_buttons_frame = ttk.Frame(status_frame)
        data_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Reset button 
        ttk.Button(data_buttons_frame, text="Reset Data", command=self.reset_data, 
                  style='Accent.TButton').pack(side=tk.LEFT, pady=5, padx=5)
        
        # Statistics button
        ttk.Button(data_buttons_frame, text="Show Statistics", 
                  command=self.show_statistics).pack(side=tk.LEFT, pady=5, padx=5)
        
        # Total rolls
        ttk.Label(status_frame, textvariable=self.total_var, font=("Arial", 10, "bold")).pack(pady=5)
        
        # Graph frame
        graph_frame = ttk.LabelFrame(self.parent, text="Dice Roll Distribution")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.graph_container = ttk.Frame(graph_frame)
        self.graph_container.pack(fill=tk.BOTH, expand=True)
        
        # Dice buttons frame
        self.dice_buttons_frame = ttk.LabelFrame(self.parent, text="Roll Dice")
        self.dice_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Initial configuration
        self.apply_config()
    
    def apply_config(self):
        """Apply the current dice configuration"""
        try:
            num_dice = int(self.num_dice.get())
            faces = int(self.dice_faces.get())
            name = self.dice_name.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a dice set name")
                return
                
            if num_dice < 1 or num_dice > 20:
                messagebox.showerror("Error", "Number of dice must be between 1 and 20")
                return
                
            if faces < 2:
                messagebox.showerror("Error", "Number of faces must be at least 2")
                return
                
            # Set current configuration
            self.dice_manager.set_current_dice(name, num_dice, faces)
            
            # Get file path
            file_path = get_file_path(name, num_dice)
            
            # Read existing rolls if any
            if num_dice == 1:
                rolls = read_single_rolls(file_path)
                self.dice_manager.current_roll = []
            else:
                rolls = read_multiple_rolls(file_path)
                self.dice_manager.current_roll = []
            
            # Update UI
            self.status_var.set(f"Ready to roll {num_dice} {'die' if num_dice == 1 else 'dice'} with {faces} faces")
            
            # Clear dice buttons
            for widget in self.dice_buttons_frame.winfo_children():
                widget.destroy()
            
            self.dice_buttons = []
            self.button_vars = {}
            self.percent_vars = {}
            
            # Create dice buttons
            button_frame = ttk.Frame(self.dice_buttons_frame)
            button_frame.pack(pady=10)
            
            # For reasonable number of buttons, show them all
            if faces <= 20:
                for val in range(1, faces + 1):
                    btn = tk.Button(button_frame, text=str(val), width=3, height=1, 
                                    font=("Arial", 14), command=lambda v=val: self.on_roll(v))
                    btn.pack(side=tk.LEFT, padx=3)
                    self.dice_buttons.append(btn)
            else:
                # For large number of faces, show entry field
                ttk.Label(button_frame, text="Enter Value (1-{}):".format(faces)).pack(side=tk.LEFT, padx=5)
                self.roll_value = tk.StringVar()
                entry = ttk.Entry(button_frame, textvariable=self.roll_value, width=5)
                entry.pack(side=tk.LEFT, padx=5)
                
                roll_btn = ttk.Button(button_frame, text="Roll", 
                                     command=self.on_roll_custom)
                roll_btn.pack(side=tk.LEFT, padx=5)
            
            # Update graph
            self.show_graph()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def on_roll(self, value):
        """Handle a dice roll"""
        num_dice = self.dice_manager.current_num_dice
        name = self.dice_manager.current_dice_set
        file_path = get_file_path(name, num_dice)
        
        if num_dice == 1:
            # Single die roll
            log_single_roll(file_path, value)
            self.status_var.set(f"Rolled: {value}")
            self.show_graph()
        else:
            # Multiple dice roll
            self.dice_manager.current_roll.append(value)
            
            if len(self.dice_manager.current_roll) < num_dice:
                self.status_var.set(f"Rolled: {', '.join(map(str, self.dice_manager.current_roll))} - {num_dice - len(self.dice_manager.current_roll)} more...")
            else:
                log_multiple_rolls(file_path, self.dice_manager.current_roll)
                self.status_var.set(f"Completed roll: {', '.join(map(str, self.dice_manager.current_roll))}")
                self.dice_manager.current_roll = []
                self.show_graph()
    
    def on_roll_custom(self):
        """Handle a custom dice roll"""
        try:
            value = int(self.roll_value.get())
            faces = self.dice_manager.current_dice_faces
            
            if value < 1 or value > faces:
                messagebox.showerror("Error", f"Value must be between 1 and {faces}")
                return
                
            self.on_roll(value)
            self.roll_value.set("")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def reset_data(self):
        """Reset the current dice data"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data for this dice set?"):
            name = self.dice_manager.current_dice_set
            num_dice = self.dice_manager.current_num_dice
            file_path = get_file_path(name, num_dice)
            
            # Delete the file instead of just clearing it
            delete_file(file_path)
            self.status_var.set("Data reset!")
            self.dice_manager.current_roll = []
            self.last_fairness_stats = None
            self.show_graph()
    
    def show_statistics(self):
        """Show detailed statistical analysis of the dice rolls"""
        if not self.last_fairness_stats:
            messagebox.showwarning("Statistics", "No roll data available. Roll some dice first.")
            return
            
        # Show statistics dialog
        StatsDialog(self.parent.master, "Dice Statistics Analysis", self.last_fairness_stats)
    
    def load_dice_set(self):
        """Load a dice set from saved data"""
        # Determine directory based on number of dice
        num_dice = self.num_dice.get()
        directory = SINGLE_DICE_DIR if num_dice == 1 else MULTIPLE_DICE_DIR
        
        # Get available sets
        sets = get_available_dice_sets(directory)
        
        if not sets:
            messagebox.showwarning("Load Set", "No saved dice sets available.")
            return
        
        # Create selection dialog
        dialog = SetSelectionDialog(self.parent.master, "Select Dice Set", sets)
        if dialog.result:
            self.dice_name.set(dialog.result)
            self.apply_config()
    
    def show_graph(self):
        """Show the dice roll distribution graph"""
        name = self.dice_manager.current_dice_set
        num_dice = self.dice_manager.current_num_dice
        faces = self.dice_manager.current_dice_faces
        file_path = get_file_path(name, num_dice)
        
        # Check if dark mode is enabled
        dark_mode = prefs.get_preference('dark_mode', False)
        
        # Colors based on dark mode
        bg_color = '#303030' if dark_mode else 'white'
        text_color = 'white' if dark_mode else 'black'
        bar_color = '#5599ff' if dark_mode else 'skyblue'
        
        # Clear existing graph
        for widget in self.graph_container.winfo_children():
            widget.destroy()
        
        # Create figure
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor(bg_color)
        
        if num_dice == 1:
            # Single die graph
            rolls = read_single_rolls(file_path)
            
            # Get fairness statistics
            alpha = prefs.get_preference('statistical_alpha', 0.05)
            self.last_fairness_stats = get_dice_fairness(rolls, faces, alpha) if rolls else None
            
            # Get dice statistics
            counts, total, percentages = self.dice_manager.calculate_statistics(rolls)
            
            # Update total and button counts
            self.total_var.set(f"Total Rolls: {total}")
            
            # Create bar chart for single die
            ax = fig.add_subplot(111)
            ax.set_facecolor(bg_color)
            face_values = list(range(1, faces + 1))
            values = [counts.get(face, 0) for face in face_values]
            bars = ax.bar([str(f) for f in face_values], values, color=bar_color)
            
            # Add percentage labels on bars
            for i, bar in enumerate(bars):
                face = face_values[i]
                height = bar.get_height()
                percent = percentages.get(face, 0.0)
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{percent:.1f}%', ha='center', va='bottom', 
                        rotation=0, fontsize=8, color=text_color)
                        
            # Add fairness indicator if we have enough data
            if self.last_fairness_stats and 'sample_validity' in self.last_fairness_stats:
                validity = self.last_fairness_stats['sample_validity']
                if validity['valid']:
                    fairness = self.last_fairness_stats['fairness_test']
                    is_fair = fairness.get('is_fair', None)
                    
                    if is_fair is not None:
                        color = 'green' if is_fair else 'red'
                        if dark_mode:
                            color = '#66ff66' if is_fair else '#ff6666'
                        
                        ax.text(0.5, 0.95, "FAIR" if is_fair else "NOT FAIR",
                               transform=ax.transAxes, ha='center', va='top',
                               color=color, fontsize=12, fontweight='bold')
                        
                        ax.text(0.5, 0.90, f"p={fairness.get('p_value', 0):.3f}",
                               transform=ax.transAxes, ha='center', va='top',
                               color=text_color, fontsize=10)
                else:
                    ax.text(0.5, 0.95, f"Need {validity['min_required']} rolls for fairness test",
                           transform=ax.transAxes, ha='center', va='top',
                           color='orange', fontsize=10)
            
            ax.set_xlabel('Dice Value', color=text_color)
            ax.set_ylabel('Count', color=text_color)
            ax.set_title(f'Dice Roll Distribution - {name}', color=text_color)
            ax.tick_params(axis='x', colors=text_color)
            ax.tick_params(axis='y', colors=text_color)
            ax.spines['bottom'].set_color(text_color)
            ax.spines['top'].set_color(text_color)
            ax.spines['left'].set_color(text_color)
            ax.spines['right'].set_color(text_color)
            
        else:
            # Multiple dice graph
            rolls = read_multiple_rolls(file_path)
            
            # Get fairness statistics
            if rolls:
                alpha = prefs.get_preference('statistical_alpha', 0.05)
                flat_rolls = [val for roll in rolls for val in roll]
                self.last_fairness_stats = get_dice_fairness(flat_rolls, faces, alpha)
            else:
                self.last_fairness_stats = None
            
            counts, total, percentages, position_stats = self.dice_manager.calculate_multi_statistics(rolls, faces)
            
            # Update total
            self.total_var.set(f"Total Rolls: {len(rolls)}")
            
            # Create subplots
            if not rolls:
                # Empty graph if no data
                ax = fig.add_subplot(111)
                ax.set_title(f"No data for {name}", color=text_color)
                ax.set_facecolor(bg_color)
                ax.tick_params(axis='x', colors=text_color)
                ax.tick_params(axis='y', colors=text_color)
            else:
                # Create grid based on number of dice
                if num_dice <= 3:
                    # For 2-3 dice: overall + individual dice
                    ax1 = fig.add_subplot(1, num_dice + 1, 1)
                    ax1.set_facecolor(bg_color)
                    face_values = list(range(1, faces + 1))
                    values = [counts.get(face, 0) for face in face_values]
                    ax1.bar([str(f) for f in face_values], values, color=bar_color)
                    ax1.set_title('Overall Distribution', color=text_color)
                    
                    # Add fairness indicator if we have enough data
                    if self.last_fairness_stats and 'sample_validity' in self.last_fairness_stats:
                        validity = self.last_fairness_stats['sample_validity']
                        if validity['valid']:
                            fairness = self.last_fairness_stats['fairness_test']
                            is_fair = fairness.get('is_fair', None)
                            
                            if is_fair is not None:
                                color = 'green' if is_fair else 'red'
                                if dark_mode:
                                    color = '#66ff66' if is_fair else '#ff6666'
                                
                                ax1.text(0.5, 0.95, "FAIR" if is_fair else "NOT FAIR",
                                       transform=ax1.transAxes, ha='center', va='top',
                                       color=color, fontsize=10, fontweight='bold')
                        else:
                            ax1.text(0.5, 0.95, f"Need more rolls for fairness test",
                                   transform=ax1.transAxes, ha='center', va='top',
                                   color='orange', fontsize=8)
                    
                    ax1.tick_params(axis='x', rotation=45, colors=text_color)
                    ax1.tick_params(axis='y', colors=text_color)
                    ax1.spines['bottom'].set_color(text_color)
                    ax1.spines['top'].set_color(text_color)
                    ax1.spines['left'].set_color(text_color)
                    ax1.spines['right'].set_color(text_color)
                    
                    for i in range(num_dice):
                        ax = fig.add_subplot(1, num_dice + 1, i + 2)
                        ax.set_facecolor(bg_color)
                        pos_counts = position_stats.get(i, {})
                        pos_values = [pos_counts.get(face, 0) for face in face_values]
                        ax.bar([str(f) for f in face_values], pos_values, color=f'C{i}')
                        ax.set_title(f'Die {i+1}', color=text_color)
                        ax.tick_params(axis='x', rotation=45, colors=text_color)
                        ax.tick_params(axis='y', colors=text_color)
                        ax.spines['bottom'].set_color(text_color)
                        ax.spines['top'].set_color(text_color)
                        ax.spines['left'].set_color(text_color)
                        ax.spines['right'].set_color(text_color)
                else:
                    # For 4+ dice: just overall + sum
                    ax1 = fig.add_subplot(1, 2, 1)
                    ax1.set_facecolor(bg_color)
                    face_values = list(range(1, faces + 1))
                    values = [counts.get(face, 0) for face in face_values]
                    ax1.bar([str(f) for f in face_values], values, color=bar_color)
                    ax1.set_title('Overall Distribution', color=text_color)
                    
                    # Add fairness indicator if we have enough data
                    if self.last_fairness_stats and 'sample_validity' in self.last_fairness_stats:
                        validity = self.last_fairness_stats['sample_validity']
                        if validity['valid']:
                            fairness = self.last_fairness_stats['fairness_test']
                            is_fair = fairness.get('is_fair', None)
                            
                            if is_fair is not None:
                                color = 'green' if is_fair else 'red'
                                if dark_mode:
                                    color = '#66ff66' if is_fair else '#ff6666'
                                
                                ax1.text(0.5, 0.95, "FAIR" if is_fair else "NOT FAIR",
                                       transform=ax1.transAxes, ha='center', va='top',
                                       color=color, fontsize=10, fontweight='bold')
                        else:
                            ax1.text(0.5, 0.95, f"Need more rolls for fairness test",
                                   transform=ax1.transAxes, ha='center', va='top',
                                   color='orange', fontsize=8)
                    
                    ax1.tick_params(axis='x', rotation=45, colors=text_color)
                    ax1.tick_params(axis='y', colors=text_color)
                    ax1.spines['bottom'].set_color(text_color)
                    ax1.spines['top'].set_color(text_color)
                    ax1.spines['left'].set_color(text_color)
                    ax1.spines['right'].set_color(text_color)
                    
                    # Sum distribution
                    ax2 = fig.add_subplot(1, 2, 2)
                    ax2.set_facecolor(bg_color)
                    sums = [sum(roll) for roll in rolls]
                    min_sum = min(sums) if sums else num_dice
                    max_sum = max(sums) if sums else num_dice * faces
                    sum_range = list(range(min_sum, max_sum + 1))
                    sum_counts = Counter(sums)
                    sum_values = [sum_counts.get(s, 0) for s in sum_range]
                    ax2.bar([str(s) for s in sum_range], sum_values, color='lightgreen')
                    ax2.set_title('Sum Distribution', color=text_color)
                    ax2.tick_params(axis='x', rotation=45, colors=text_color)
                    ax2.tick_params(axis='y', colors=text_color)
                    ax2.spines['bottom'].set_color(text_color)
                    ax2.spines['top'].set_color(text_color)
                    ax2.spines['left'].set_color(text_color)
                    ax2.spines['right'].set_color(text_color)
        
        fig.tight_layout()
        
        # Add graph to container
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
