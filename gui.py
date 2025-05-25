import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import os

from dice_manager import DiceManager
from file_utils import (
    ensure_directories, get_file_path, log_single_roll, log_multiple_rolls,
    read_single_rolls, read_multiple_rolls, reset_file, get_available_dice_sets,
    SINGLE_DICE_DIR, MULTIPLE_DICE_DIR
)
from simulation import DiceSimulator

class DiceTrackerApp:
    """Main application class for Dice Tracker"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Dice Roll Tracker")
        self.root.geometry("800x600")
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize dice manager
        self.dice_manager = DiceManager()
        
        # UI variables
        self.num_dice = tk.IntVar(value=1)
        self.dice_faces = tk.IntVar(value=6)
        self.dice_name = tk.StringVar(value="Default")
        self.status_var = tk.StringVar(value="Ready to roll!")
        self.total_var = tk.StringVar(value="")
        
        # UI components
        self.canvas = None
        self.button_vars = {}
        self.percent_vars = {}
        self.dice_buttons = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab frames
        roller_frame = ttk.Frame(notebook)
        simulator_frame = ttk.Frame(notebook)
        
        notebook.add(roller_frame, text="Dice Roller")
        notebook.add(simulator_frame, text="Dice Simulator")
        
        # Setup the roller tab
        self.setup_roller_tab(roller_frame)
        
        # Setup the simulator tab
        self.setup_simulator_tab(simulator_frame)
    
    def setup_roller_tab(self, parent):
        """Setup the dice roller tab"""
        # Top frame for configuration
        top_frame = ttk.Frame(parent)
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
        faces_values = [3, 4, 6, 8, 10, 12, 20, 100]
        faces_cb = ttk.Combobox(faces_frame, values=faces_values, width=5, 
                               textvariable=self.dice_faces)
        faces_cb.pack(side=tk.LEFT, padx=5)
        faces_cb.set("6")
        
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
        
        # Reset button 
        ttk.Button(status_frame, text="Reset Data", command=self.reset_data, style='Accent.TButton').pack(pady=5)
        
        # Total rolls
        ttk.Label(status_frame, textvariable=self.total_var, font=("Arial", 10, "bold")).pack(pady=5)
        
        # Graph frame
        graph_frame = ttk.LabelFrame(parent, text="Dice Roll Distribution")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.graph_container = ttk.Frame(graph_frame)
        self.graph_container.pack(fill=tk.BOTH, expand=True)
        
        # Dice buttons frame
        self.dice_buttons_frame = ttk.LabelFrame(parent, text="Roll Dice")
        self.dice_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Initial configuration
        self.apply_config()
    
    def setup_simulator_tab(self, parent):
        """Setup the dice simulator tab"""
        # Simulation configuration
        config_frame = ttk.LabelFrame(parent, text="Simulation Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Number of dice
        dice_frame = ttk.Frame(config_frame)
        dice_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dice_frame, text="Number of dice:").pack(side=tk.LEFT, padx=5)
        self.sim_num_dice = tk.IntVar(value=1)
        ttk.Spinbox(dice_frame, from_=1, to=20, width=5, 
                    textvariable=self.sim_num_dice).pack(side=tk.LEFT, padx=5)
        
        # Number of faces
        faces_frame = ttk.Frame(config_frame)
        faces_frame.pack(fill=tk.X, pady=5)
        ttk.Label(faces_frame, text="Number of faces:").pack(side=tk.LEFT, padx=5)
        self.sim_faces = tk.IntVar(value=6)
        faces_values = [3, 4, 6, 8, 10, 12, 20, 100]
        faces_cb = ttk.Combobox(faces_frame, values=faces_values, width=5, 
                               textvariable=self.sim_faces)
        faces_cb.pack(side=tk.LEFT, padx=5)
        faces_cb.set("6")
        
        # Number of rolls
        rolls_frame = ttk.Frame(config_frame)
        rolls_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rolls_frame, text="Number of rolls:").pack(side=tk.LEFT, padx=5)
        self.sim_num_rolls = tk.IntVar(value=30)
        ttk.Spinbox(rolls_frame, from_=1, to=1000, width=5, 
                    textvariable=self.sim_num_rolls).pack(side=tk.LEFT, padx=5)
        
        # Dice set name
        name_frame = ttk.Frame(config_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Dice Set Name:").pack(side=tk.LEFT, padx=5)
        self.sim_name = tk.StringVar(value="Simulation")
        ttk.Entry(name_frame, textvariable=self.sim_name, width=20).pack(side=tk.LEFT, padx=5)
        
        # Run simulation button
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Run Simulation", 
                   command=self.run_simulation).pack(padx=5)
        
        # Graph frame
        self.sim_graph_frame = ttk.LabelFrame(parent, text="Simulation Results")
        self.sim_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sim_graph_container = ttk.Frame(self.sim_graph_frame)
        self.sim_graph_container.pack(fill=tk.BOTH, expand=True)
    
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
            
            reset_file(file_path)
            self.status_var.set("Data reset!")
            self.dice_manager.current_roll = []
            self.show_graph()
    
    def load_dice_set(self):
        """Load a dice set from saved data"""
        # Determine directory based on number of dice
        num_dice = self.num_dice.get()
        directory = SINGLE_DICE_DIR if num_dice == 1 else MULTIPLE_DICE_DIR
        
        # Get available sets
        sets = get_available_dice_sets(directory)
        
        if not sets:
            messagebox.showinfo("Info", f"No saved dice sets found for {num_dice} {'die' if num_dice == 1 else 'dice'}")
            return
        
        # Create selection dialog
        dialog = SetSelectionDialog(self.root, "Select Dice Set", sets)
        if dialog.result:
            self.dice_name.set(dialog.result)
            self.apply_config()
    
    def show_graph(self):
        """Show the dice roll distribution graph"""
        name = self.dice_manager.current_dice_set
        num_dice = self.dice_manager.current_num_dice
        faces = self.dice_manager.current_dice_faces
        file_path = get_file_path(name, num_dice)
        
        # Clear existing graph
        for widget in self.graph_container.winfo_children():
            widget.destroy()
        
        # Create figure
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        
        if num_dice == 1:
            # Single die graph
            rolls = read_single_rolls(file_path)
            counts, total, percentages = self.dice_manager.calculate_statistics(rolls)
            
            # Update total and button counts
            self.total_var.set(f"Total Rolls: {total}")
            
            # Create bar chart for single die
            ax = fig.add_subplot(111)
            face_values = list(range(1, faces + 1))
            values = [counts.get(face, 0) for face in face_values]
            bars = ax.bar([str(f) for f in face_values], values, color='skyblue')
            
            # Add percentage labels on bars
            for i, bar in enumerate(bars):
                face = face_values[i]
                height = bar.get_height()
                percent = percentages.get(face, 0.0)
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{percent:.1f}%', ha='center', va='bottom', rotation=0, fontsize=8)
            
            ax.set_xlabel('Dice Value')
            ax.set_ylabel('Count')
            ax.set_title(f'Dice Roll Distribution - {name}')
            
        else:
            # Multiple dice graph
            rolls = read_multiple_rolls(file_path)
            counts, total, percentages, position_stats = self.dice_manager.calculate_multi_statistics(rolls, faces)
            
            # Update total
            self.total_var.set(f"Total Rolls: {len(rolls)}")
            
            # Create subplots
            if not rolls:
                # Empty graph if no data
                ax = fig.add_subplot(111)
                ax.set_title(f"No data for {name}")
            else:
                # Create grid based on number of dice
                if num_dice <= 3:
                    # For 2-3 dice: overall + individual dice
                    ax1 = fig.add_subplot(1, num_dice + 1, 1)
                    face_values = list(range(1, faces + 1))
                    values = [counts.get(face, 0) for face in face_values]
                    ax1.bar([str(f) for f in face_values], values, color='skyblue')
                    ax1.set_title('Overall Distribution')
                    ax1.tick_params(axis='x', rotation=45)
                    
                    for i in range(num_dice):
                        ax = fig.add_subplot(1, num_dice + 1, i + 2)
                        pos_counts = position_stats.get(i, {})
                        pos_values = [pos_counts.get(face, 0) for face in face_values]
                        ax.bar([str(f) for f in face_values], pos_values, color=f'C{i}')
                        ax.set_title(f'Die {i+1}')
                        ax.tick_params(axis='x', rotation=45)
                else:
                    # For 4+ dice: just overall + sum
                    ax1 = fig.add_subplot(1, 2, 1)
                    face_values = list(range(1, faces + 1))
                    values = [counts.get(face, 0) for face in face_values]
                    ax1.bar([str(f) for f in face_values], values, color='skyblue')
                    ax1.set_title('Overall Distribution')
                    ax1.tick_params(axis='x', rotation=45)
                    
                    # Sum distribution
                    ax2 = fig.add_subplot(1, 2, 2)
                    sums = [sum(roll) for roll in rolls]
                    min_sum = min(sums) if sums else num_dice
                    max_sum = max(sums) if sums else num_dice * faces
                    sum_range = list(range(min_sum, max_sum + 1))
                    sum_counts = Counter(sums)
                    sum_values = [sum_counts.get(s, 0) for s in sum_range]
                    ax2.bar([str(s) for s in sum_range], sum_values, color='lightgreen')
                    ax2.set_title('Sum Distribution')
                    ax2.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        
        # Add graph to container
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def run_simulation(self):
        """Run a dice simulation"""
        try:
            num_dice = self.sim_num_dice.get()
            faces = self.sim_faces.get()
            num_rolls = self.sim_num_rolls.get()
            name = self.sim_name.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a dice set name")
                return
                
            if num_dice < 1 or num_rolls < 1 or faces < 2:
                messagebox.showerror("Error", "Invalid simulation parameters")
                return
            
            # Run simulation
            simulated_rolls = DiceSimulator.simulate_rolls(num_rolls, num_dice, faces)
            
            # Save results
            file_path = get_file_path(name, num_dice)
            if num_dice == 1:
                # Flatten for single die rolls
                for roll in simulated_rolls:
                    log_single_roll(file_path, roll[0])
            else:
                # Multiple dice rolls
                for roll in simulated_rolls:
                    log_multiple_rolls(file_path, roll)
            
            # Show graph
            self.show_simulation_results(simulated_rolls, faces)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def show_simulation_results(self, rolls, faces):
        """Show the simulation results"""
        # Clear existing graph
        for widget in self.sim_graph_container.winfo_children():
            widget.destroy()
        
        # Create simulation figure
        fig = DiceSimulator.create_simulation_figure(rolls, faces)
        
        # Add title
        fig.suptitle(f"Simulation Results: {len(rolls)} rolls of {len(rolls[0]) if rolls else 0} {faces}-sided dice")
        
        # Add graph to container
        canvas = FigureCanvasTkAgg(fig, master=self.sim_graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class SetSelectionDialog:
    """Dialog for selecting a dice set"""
    
    def __init__(self, parent, title, options):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Select a dice set:").pack(padx=10, pady=(10, 0))
        
        # Listbox with options
        self.listbox = tk.Listbox(dialog, width=40, height=8)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        for option in options:
            self.listbox.insert(tk.END, option)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Make dialog modal
        dialog.grab_set()
        parent.wait_window(dialog)
    
    def on_ok(self):
        """Handle OK button click"""
        selection = self.listbox.curselection()
        if selection:
            self.result = self.listbox.get(selection[0])
        self.listbox.master.destroy()
