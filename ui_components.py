"""
UI components and dialogs for DiceGraph application.
Contains reusable UI elements and dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable, Dict, Any, Union

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
