"""
Dice simulator implementation for the DiceGraph application.
Handles the dice simulation tab functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from dice_manager import DiceManager
from file_utils import (
    get_file_path, log_single_roll, log_multiple_rolls, reset_file,
    get_simulation_file_path, get_available_simulations, SIMULATION_DIR
)
from simulation import DiceSimulator
import user_preferences as prefs
from ui_components import ConfirmationDialog, SetSelectionDialog, StatsDialog

class DiceSimulatorTab:
    """Class to manage the dice simulator tab in the application"""
    
    def __init__(self, parent, app_instance):
        """
        Initialize the dice simulator tab.
        
        Args:
            parent: The parent frame
            app_instance: The main application instance
        """
        self.parent = parent
        self.app = app_instance
        self.dice_manager = app_instance.dice_manager
        self.status_var = app_instance.status_var
        
        # Simulation variables
        self.sim_num_dice = tk.IntVar(value=1)
        self.sim_faces = tk.IntVar(value=app_instance.dice_faces.get())
        self.sim_num_rolls = tk.IntVar(value=30)
        self.sim_name = tk.StringVar(value="Simulation")
        
        # UI components
        self.sim_canvas = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the simulator tab UI"""
        # Simulation configuration
        config_frame = ttk.LabelFrame(self.parent, text="Simulation Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Number of dice
        dice_frame = ttk.Frame(config_frame)
        dice_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dice_frame, text="Number of dice:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(dice_frame, from_=1, to=20, width=5, 
                    textvariable=self.sim_num_dice).pack(side=tk.LEFT, padx=5)
        
        # Number of faces
        faces_frame = ttk.Frame(config_frame)
        faces_frame.pack(fill=tk.X, pady=5)
        ttk.Label(faces_frame, text="Number of faces:").pack(side=tk.LEFT, padx=5)
        # Use Spinbox for faces
        faces_spin = ttk.Spinbox(faces_frame, from_=2, to=100, width=5, textvariable=self.sim_faces)
        faces_spin.pack(side=tk.LEFT, padx=5)
        faces_spin.set(str(prefs.get_preference('default_faces', 6)))
        
        # Number of rolls
        rolls_frame = ttk.Frame(config_frame)
        rolls_frame.pack(fill=tk.X, pady=5)
        ttk.Label(rolls_frame, text="Number of rolls:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(rolls_frame, from_=1, to=10000, width=5, 
                    textvariable=self.sim_num_rolls).pack(side=tk.LEFT, padx=5)
        
        # Dice set name
        name_frame = ttk.Frame(config_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="Simulation Name:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(name_frame, textvariable=self.sim_name, width=20).pack(side=tk.LEFT, padx=5)
          # Button frame
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Run simulation button
        ttk.Button(button_frame, text="Run Simulation", 
                  command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        
        # Load simulation button
        ttk.Button(button_frame, text="Load Simulation", 
                  command=self.load_simulation).pack(side=tk.LEFT, padx=5)
                  
        # Reset button
        ttk.Button(button_frame, text="Reset", style='Accent.TButton',
                  command=self.reset_simulation).pack(side=tk.LEFT, padx=5)
        
        # Statistics button
        ttk.Button(button_frame, text="Show Statistics", 
                  command=self.show_statistics).pack(side=tk.RIGHT, padx=5)
        
        # Graph frame
        self.sim_graph_frame = ttk.LabelFrame(self.parent, text="Simulation Results")
        self.sim_graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sim_graph_container = ttk.Frame(self.sim_graph_frame)
        self.sim_graph_container.pack(fill=tk.BOTH, expand=True)
        
        # Store the last simulation for stats
        self.last_simulation = None
        self.last_fairness_stats = None
    
    def run_simulation(self):
        """Run a dice simulation"""
        try:
            num_dice = self.sim_num_dice.get()
            faces = self.sim_faces.get()
            num_rolls = self.sim_num_rolls.get()
            name = self.sim_name.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a simulation name")
                return
                
            if num_dice < 1 or num_rolls < 1 or faces < 2:
                messagebox.showerror("Error", "Invalid simulation parameters")
                return
            
            # Show warning for large simulations
            if num_rolls > 999:
                dialog = ConfirmationDialog(
                    self.parent.master,
                    "Large Simulation",
                    f"You are about to run a simulation with {num_rolls} rolls.\n"
                    "This may take some time to complete.\n\nDo you want to continue?",
                    "Continue", "Cancel"
                )
                if not dialog.result:
                    return
            
            # Run simulation
            self.status_var.set(f"Running simulation with {num_dice} dice, {faces} faces, {num_rolls} rolls...")
            self.parent.update()  # Update UI to show status
            
            # Simulate rolls
            simulated_rolls = DiceSimulator.simulate_rolls(num_rolls, num_dice, faces)
            
            # Save results to simulation directory
            file_path = get_simulation_file_path(name, num_dice, faces, num_rolls)
            
            # Save in simulation format
            with open(file_path, 'w') as f:
                for roll in simulated_rolls:
                    f.write(f"{','.join(map(str, roll))}\n")
            
            # Store the simulation
            self.last_simulation = simulated_rolls
            
            # Show simulation results
            self.show_simulation_results(simulated_rolls, faces)
              self.status_var.set(f"Simulation complete: {num_rolls} rolls of {num_dice} {faces}-sided dice")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            
    def load_simulation(self):
        """Load a simulation from saved files"""
        # Get available simulations
        simulations = get_available_simulations()
        
        if not simulations:
            messagebox.showwarning("Load Simulation", "No saved simulations available.")
            return
        
        # Extract just the simulation names for display
        sim_names = [f"{sim['num_dice']} dice, {sim['faces']} faces, {sim['num_rolls']} rolls - {sim['name']}" 
                    for sim in simulations]
        
        # Create selection dialog only if we have simulations available
        dialog = SetSelectionDialog(self.parent.master, "Select Simulation", sim_names)
        if dialog.result:
            # Find the selected simulation
            idx = sim_names.index(dialog.result)
            selected_sim = simulations[idx]
            
            # Update UI with the simulation parameters
            self.sim_num_dice.set(selected_sim['num_dice'])
            self.sim_faces.set(selected_sim['faces'])
            self.sim_num_rolls.set(selected_sim['num_rolls'])
            self.sim_name.set(selected_sim['name'])
            
            # Load the simulation data
            with open(selected_sim['full_path'], 'r') as f:
                lines = f.readlines()
                
            rolls = [list(map(int, line.strip().split(','))) for line in lines if line.strip()]
            
            # Store the simulation
            self.last_simulation = rolls
            
            # Show simulation results
            self.show_simulation_results(rolls, selected_sim['faces'])
            
            self.status_var.set(f"Loaded simulation: {selected_sim['num_rolls']} rolls of "
                               f"{selected_sim['num_dice']} {selected_sim['faces']}-sided dice")
    
    def reset_simulation(self):
        """Reset the simulation tab and clear results"""
        if self.last_simulation and messagebox.askyesno("Confirm Reset", 
                                                    "Are you sure you want to clear the current simulation results?"):
            # Clear the graph
            for widget in self.sim_graph_container.winfo_children():
                widget.destroy()
                
            self.last_simulation = None
            self.last_fairness_stats = None
            self.status_var.set("Simulation results cleared")
    
    def show_statistics(self):
        """Show detailed statistical analysis of the simulation"""
        if not self.last_simulation:
            messagebox.showwarning("Statistics", "No simulation data available. Run or load a simulation first.")
            return
            
        # Show statistics dialog
        StatsDialog(self.parent.master, "Dice Statistics Analysis", self.last_fairness_stats)
    
    def show_simulation_results(self, rolls, faces):
        """Show the simulation results"""
        # Clear existing graph
        for widget in self.sim_graph_container.winfo_children():
            widget.destroy()
        
        # Check if dark mode is enabled
        dark_mode = prefs.get_preference('dark_mode', False)
        
        # Create simulation figure with fairness statistics
        fig, fairness_stats = DiceSimulator.create_simulation_figure(rolls, faces, dark_mode)
        
        # Store fairness stats for later use
        self.last_fairness_stats = fairness_stats
        
        # Add title
        fig.suptitle(f"Simulation Results: {len(rolls)} rolls of {len(rolls[0]) if rolls else 0} {faces}-sided dice")
        
        # Add graph to container
        canvas = FigureCanvasTkAgg(fig, master=self.sim_graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
