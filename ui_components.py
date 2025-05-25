"""
UI components and dialogs for DiceGraph application.
Contains reusable UI elements and dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable, Dict, Any, Union
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import user_preferences as prefs

class SetSelectionDialog:
    """
    Dialog for selecting a dice set from a list.
    """
    
    def __init__(self, parent: tk.Tk, title: str, options: List[str]):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent window
            title: The dialog title
            options: List of options to select from
        """
        self.result = None
        
        # Don't create dialog if no options
        if not options:
            return
        
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


class ConfirmationDialog:
    """
    Dialog for confirming an action, especially for potentially time-consuming operations.
    """
    
    def __init__(self, parent: tk.Tk, title: str, message: str, 
                 continue_text: str = "Continue", cancel_text: str = "Cancel"):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent window
            title: The dialog title
            message: The message to display
            continue_text: Text for the continue button
            cancel_text: Text for the cancel button
        """
        self.result = False
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # Message
        ttk.Label(dialog, text=message, wraplength=320, justify=tk.CENTER).pack(padx=15, pady=15)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(button_frame, text=continue_text, command=self.on_continue).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text=cancel_text, command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Make dialog modal
        dialog.grab_set()
        parent.wait_window(dialog)
    
    def on_continue(self):
        """Handle Continue button click"""
        self.result = True
        self.result = True
        self.listbox.master.destroy() if hasattr(self, 'listbox') else self._root().destroy()


class StatsDialog:
    """
    Dialog for displaying statistical analysis results.
    """
    
    def __init__(self, parent: tk.Tk, title: str, stats_data: Dict[str, Any]):
        """
        Initialize the dialog.
        
        Args:
            parent: The parent window
            title: The dialog title
            stats_data: Dictionary containing statistical analysis results
        """
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different statistical views
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Summary")
          # Get fairness test data
        fairness = stats_data.get('fairness_test', {})
        conclusion = fairness.get('conclusion', 'Insufficient data for analysis')
        p_value = fairness.get('p_value', 0)
        is_fair = fairness.get('is_fair', True)
        alpha = fairness.get('alpha', 0.05)
        chi2_stat = fairness.get('chi2_stat', 0)
        significance = fairness.get('significance', '')
        
        # Display summary
        summary_text = (
            f"Total Rolls: {stats_data.get('total_rolls', 0)}\n\n"
            f"Fairness Test Result:\n{conclusion}\n\n"
            f"Chi-square test statistic: {chi2_stat:.4f}\n"
            f"P-value: {p_value:.4f}\n"
            f"Significance level (α): {alpha:.3f}\n\n"
            f"{significance}\n\n"
            f"The dice {'appear to be fair' if is_fair else 'may not be fair'}"
        )
        
        summary_label = ttk.Label(
            summary_frame, 
            text=summary_text,
            justify=tk.LEFT,
            wraplength=460
        )
        summary_label.pack(padx=10, pady=10, anchor=tk.NW)
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Details")
        
        # Create a text widget for detailed stats
        details_text = tk.Text(details_frame, wrap=tk.WORD, height=20, width=60)
        details_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(details_text, command=details_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_text.config(yscrollcommand=scrollbar.set)
        
        # Format detailed statistics
        face_counts = stats_data.get('face_counts', {})
        face_percentages = stats_data.get('face_percentages', {})
        
        details_text.insert(tk.END, "Individual Face Statistics:\n\n")
        
        for face in sorted(face_counts.keys()):
            count = face_counts.get(face, 0)
            percentage = face_percentages.get(face, 0)
            details_text.insert(tk.END, f"Face {face}: {count} rolls ({percentage:.2f}%)\n")
        
        details_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=dialog.destroy).pack(pady=10)


class SumDistributionWindow:
    """
    Window to display detailed sum distribution for dice rolls.
    """
    
    def __init__(self, parent: tk.Tk, title: str, rolls: List[List[int]], dark_mode: bool = False):
        """
        Initialize the sum distribution window.
        
        Args:
            parent: The parent window
            title: The window title
            rolls: List of dice rolls (each roll is a list of dice values)
            dark_mode: Whether to use dark mode
        """
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.minsize(700, 500)
        self.window.geometry("800x600")
        
        # Store variables
        self.rolls = rolls
        self.dark_mode = dark_mode
        
        # Calculate sum statistics
        self.calculate_sum_stats()
        
        # Setup UI
        self.setup_ui()
    
    def calculate_sum_stats(self):
        """Calculate statistics about the sum distribution"""
        if not self.rolls or not self.rolls[0]:
            self.sums = []
            self.sum_stats = {
                "count": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "mode": 0,
                "std_dev": 0
            }
            return
            
        # Calculate sums for each roll
        self.sums = [sum(roll) for roll in self.rolls]
        
        # Basic statistics
        self.sum_stats = {
            "count": len(self.sums),
            "min": min(self.sums),
            "max": max(self.sums),
            "mean": sum(self.sums) / len(self.sums) if self.sums else 0,
            "median": sorted(self.sums)[len(self.sums)//2] if self.sums else 0,
            "std_dev": np.std(self.sums) if self.sums else 0
        }
        
        # Calculate mode (most common sum)
        counter = Counter(self.sums)
        self.sum_stats["mode"] = counter.most_common(1)[0][0] if counter else 0
        
        # Calculate theoretical probabilities for standard dice
        num_dice = len(self.rolls[0]) if self.rolls and self.rolls[0] else 0
        if num_dice > 0 and all(len(roll) == num_dice for roll in self.rolls):
            # Check if we're using standard dice (all dice have the same number of faces)
            faces_per_die = [max(die_values) for die_values in zip(*self.rolls)]
            if len(set(faces_per_die)) == 1:  # All dice have the same number of faces
                num_faces = faces_per_die[0]
                # For standard dice (d6), we can calculate theoretical probabilities
                if num_faces == 6:
                    self.sum_stats["is_standard_dice"] = True
                    self.sum_stats["num_dice"] = num_dice
                    self.sum_stats["num_faces"] = num_faces
                    self.sum_stats["theoretical_mean"] = num_dice * (num_faces + 1) / 2
                    self.sum_stats["theoretical_std_dev"] = np.sqrt(num_dice * ((num_faces**2 - 1) / 12))
    
    def setup_ui(self):
        """Setup the window UI"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Colors based on dark mode
        bg_color = '#303030' if self.dark_mode else 'white'
        text_color = 'white' if self.dark_mode else 'black'
        bar_color = '#5599ff' if self.dark_mode else 'skyblue'
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(main_frame, text="Distribution Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create grid for statistics
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Add statistics labels
        row = 0
        stats_labels = [
            ("Number of Rolls:", f"{self.sum_stats['count']}"),
            ("Minimum Sum:", f"{self.sum_stats['min']}"),
            ("Maximum Sum:", f"{self.sum_stats['max']}"),
            ("Mean:", f"{self.sum_stats['mean']:.2f}"),
            ("Median:", f"{self.sum_stats['median']}"),
            ("Mode:", f"{self.sum_stats['mode']}"),
            ("Standard Deviation:", f"{self.sum_stats['std_dev']:.2f}")
        ]
        
        # Add theoretical values if available
        if self.sum_stats.get("is_standard_dice", False):
            stats_labels.extend([
                ("Theoretical Mean:", f"{self.sum_stats['theoretical_mean']:.2f}"),
                ("Theoretical Std Dev:", f"{self.sum_stats['theoretical_std_dev']:.2f}")
            ])
        
        # Create a two-column grid of labels for statistics
        col = 0
        for label, value in stats_labels:
            ttk.Label(stats_grid, text=label, font=("Arial", 10, "bold")).grid(
                row=row, column=col*2, sticky="e", padx=5, pady=3)
            ttk.Label(stats_grid, text=value).grid(
                row=row, column=col*2+1, sticky="w", padx=5, pady=3)
            
            col += 1
            if col >= 2:  # Two columns per row
                col = 0
                row += 1
        
        # Graph panel
        graph_frame = ttk.LabelFrame(main_frame, text="Sum Distribution")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure for sum distribution
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor(bg_color)
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg_color)
        
        if self.sums:
            # Create histogram of sums
            min_sum = self.sum_stats["min"]
            max_sum = self.sum_stats["max"]
            sum_range = list(range(min_sum, max_sum + 1))
            
            # Count occurrences of each sum
            sum_counts = Counter(self.sums)
            sum_values = [sum_counts.get(s, 0) for s in sum_range]
            
            # Bar chart
            bars = ax.bar([str(s) for s in sum_range], sum_values, color=bar_color)
            
            # Add percentage labels on top of bars
            total_rolls = len(self.sums)
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:
                    percentage = (height / total_rolls) * 100
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{percentage:.1f}%', ha='center', va='bottom', 
                            rotation=0, fontsize=8, color=text_color)
            
            # Add mean line
            if total_rolls > 0:
                ax.axvline(
                    x=sum_range.index(round(self.sum_stats["mean"])),
                    color='red', linestyle='--', linewidth=1,
                    label=f'Mean: {self.sum_stats["mean"]:.2f}'
                )
                
                # Add theoretical mean line if available
                if self.sum_stats.get("is_standard_dice", False):
                    theo_mean = self.sum_stats["theoretical_mean"]
                    if min_sum <= theo_mean <= max_sum:
                        # Find the closest sum value to the theoretical mean
                        closest_sum = min(sum_range, key=lambda x: abs(x - theo_mean))
                        closest_index = sum_range.index(closest_sum)
                        
                        ax.axvline(
                            x=closest_index, 
                            color='green', linestyle=':', linewidth=1,
                            label=f'Theoretical Mean: {theo_mean:.2f}'
                        )
                
                ax.legend()
            
            # Add title and labels
            ax.set_title('Dice Sum Distribution', color=text_color)
            ax.set_xlabel('Sum', color=text_color)
            ax.set_ylabel('Frequency', color=text_color)
            
        else:
            # No data
            ax.text(0.5, 0.5, "No dice roll data available", 
                   ha='center', va='center', color=text_color, fontsize=14)
        
        # Style the axes
        ax.tick_params(axis='x', colors=text_color, rotation=45)
        ax.tick_params(axis='y', colors=text_color)
        ax.spines['bottom'].set_color(text_color)
        ax.spines['top'].set_color(text_color)
        ax.spines['left'].set_color(text_color)
        ax.spines['right'].set_color(text_color)
        
        # Add grid for readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add graph to container
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button panel at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        # Close button
        ttk.Button(
            button_frame, text="Close", 
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
