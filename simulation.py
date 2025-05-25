from typing import List, Dict, Tuple
import random
import matplotlib.pyplot as plt
from collections import Counter

class DiceSimulator:
    """Class to handle dice simulations"""
    
    @staticmethod
    def simulate_rolls(num_rolls: int, num_dice: int, faces: int = 6) -> List[List[int]]:
        """Simulate multiple rolls of multiple dice"""
        results = []
        for _ in range(num_rolls):
            roll = [random.randint(1, faces) for _ in range(num_dice)]
            results.append(roll)
        return results
    
    @staticmethod
    def create_simulation_figure(rolls: List[List[int]], faces: int) -> plt.Figure:
        """Create a figure for simulated dice rolls"""
        # Calculate overall distribution
        all_values = [v for roll in rolls for v in roll]
        counts = Counter(all_values)
        
        # Prepare the figure
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        
        # Plot overall distribution
        ax1 = fig.add_subplot(121)
        face_values = list(range(1, faces + 1))
        values = [counts.get(face, 0) for face in face_values]
        ax1.bar([str(f) for f in face_values], values, color='skyblue')
        ax1.set_title('Overall Dice Value Distribution')
        ax1.set_xlabel('Dice Value')
        ax1.set_ylabel('Count')
        
        # Plot sum distribution if multiple dice
        if rolls and len(rolls[0]) > 1:
            ax2 = fig.add_subplot(122)
            sums = [sum(roll) for roll in rolls]
            min_sum = min(sums)
            max_sum = max(sums)
            sum_range = list(range(min_sum, max_sum + 1))
            sum_counts = Counter(sums)
            sum_values = [sum_counts.get(s, 0) for s in sum_range]
            ax2.bar([str(s) for s in sum_range], sum_values, color='lightgreen')
            ax2.set_title('Sum Distribution')
            ax2.set_xlabel('Sum Value')
            ax2.set_ylabel('Count')
            
        fig.tight_layout()
        return fig
