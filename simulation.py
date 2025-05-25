from typing import List, Dict, Tuple, Optional
import random
import matplotlib.pyplot as plt
from collections import Counter
import user_preferences as prefs
from statistics_utils import chi_square_test, interpret_chi_square_result, get_dice_fairness

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
    def create_simulation_figure(rolls: List[List[int]], faces: int, dark_mode: bool = False) -> Tuple[plt.Figure, Dict]:
        """
        Create a figure for simulated dice rolls and return fairness statistics
        
        Args:
            rolls: List of dice rolls
            faces: Number of faces on dice
            dark_mode: Whether to use dark mode color scheme
            
        Returns:
            Tuple of (Figure, fairness_statistics)
        """
        # Calculate overall distribution
        all_values = [v for roll in rolls for v in roll]
        counts = Counter(all_values)
        
        # Color scheme based on dark mode
        bg_color = '#303030' if dark_mode else 'white'
        text_color = 'white' if dark_mode else 'black'
        bar_colors = {
            'dice': '#5599ff' if dark_mode else 'skyblue',
            'sum': '#66bb66' if dark_mode else 'lightgreen'
        }
        
        # Prepare the figure
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor(bg_color)
        
        # Plot overall distribution
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(bg_color)
        face_values = list(range(1, faces + 1))
        values = [counts.get(face, 0) for face in face_values]
        bars1 = ax1.bar([str(f) for f in face_values], values, color=bar_colors['dice'])
        
        # Add labels and styling
        ax1.set_title('Overall Dice Value Distribution', color=text_color)
        ax1.set_xlabel('Dice Value', color=text_color)
        ax1.set_ylabel('Count', color=text_color)
        ax1.tick_params(axis='x', colors=text_color)
        ax1.tick_params(axis='y', colors=text_color)
        ax1.spines['bottom'].set_color(text_color)
        ax1.spines['top'].set_color(text_color)
        ax1.spines['left'].set_color(text_color)
        ax1.spines['right'].set_color(text_color)
          # Plot sum distribution
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(bg_color)
        
        if rolls and len(rolls[0]) > 1:
            # For multiple dice, show sum distribution
            sums = [sum(roll) for roll in rolls]
            min_sum = min(sums)
            max_sum = max(sums)
            sum_range = list(range(min_sum, max_sum + 1))
            sum_counts = Counter(sums)
            sum_values = [sum_counts.get(s, 0) for s in sum_range]
            bars2 = ax2.bar([str(s) for s in sum_range], sum_values, color=bar_colors['sum'])
            
            ax2.set_title('Sum Distribution', color=text_color)
            ax2.set_xlabel('Sum Value', color=text_color)
            ax2.set_ylabel('Count', color=text_color)
            
            # Highlight expected most common sum for fair dice (if applicable)
            if len(rolls[0]) > 1 and faces == 6:  # For standard dice
                expected_peak = len(rolls[0]) * (faces + 1) / 2  # For d6, average is 3.5 per die
                for i, s in enumerate(sum_range):
                    if abs(s - expected_peak) < 0.5:  # Highlight the peak value
                        bars2[i].set_color('#ff9966' if dark_mode else 'orange')
                        break
                
                # Add note about expected distribution
                ax2.text(0.5, 0.95, f"Expected peak: ~{expected_peak:.1f}",
                         transform=ax2.transAxes, ha='center', color=text_color,
                         fontsize=8)
        else:
            # For single die, show fairness statistics
            ax2.set_title('Fairness Analysis', color=text_color)
            ax2.set_axis_off()  # Hide the axes
            
            # Calculate fairness statistics
            alpha = prefs.get_preference('statistical_alpha', 0.05)
            stats_data = get_dice_fairness(all_values, faces, alpha)
            fairness = stats_data['fairness_test']
            
            # Text for fairness analysis
            conclusion = fairness['conclusion']
            p_value = fairness['p_value']
            is_fair = fairness['is_fair']
              # Display text on the plot
            text_y = 0.7
            ax2.text(0.5, text_y, "Fairness Analysis", 
                     ha='center', va='center', color=text_color, 
                     fontsize=14, fontweight='bold')
            
            ax2.text(0.5, text_y - 0.15, conclusion,
                     ha='center', va='center', color=text_color,
                     fontsize=11, wrap=True)
            
            # Add significance info
            significance = fairness.get('significance', '')
            ax2.text(0.5, text_y - 0.25, f"P-value: {p_value:.4f}",
                     ha='center', va='center', color=text_color,
                     fontsize=11)
            
            ax2.text(0.5, text_y - 0.35, f"α: {fairness.get('alpha', 0.05):.3f}",
                     ha='center', va='center', color=text_color,
                     fontsize=11)
                     
            color = 'green' if is_fair else 'red'
            if dark_mode:
                color = '#66ff66' if is_fair else '#ff6666'
                
            ax2.text(0.5, text_y - 0.5, "FAIR" if is_fair else "NOT FAIR",
                     ha='center', va='center', color=color,
                     fontsize=16, fontweight='bold')
        
        # Style the second plot
        ax2.tick_params(axis='x', colors=text_color)
        ax2.tick_params(axis='y', colors=text_color)
        ax2.spines['bottom'].set_color(text_color)
        ax2.spines['top'].set_color(text_color)
        ax2.spines['left'].set_color(text_color)
        ax2.spines['right'].set_color(text_color)
            
        fig.tight_layout()
        
        # Calculate fairness statistics for return
        alpha = prefs.get_preference('statistical_alpha', 0.05)
        fairness_stats = get_dice_fairness(all_values, faces, alpha)
        
        return fig, fairness_stats
