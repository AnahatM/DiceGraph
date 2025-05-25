import random
from collections import Counter
from typing import List, Dict, Tuple, Optional

class DiceManager:
    """Class to manage dice operations"""
    
    def __init__(self):
        self.current_dice_set = None
        self.current_num_dice = 1
        self.current_dice_faces = 6
        self.current_roll = []
        
    def roll_die(self, faces: int = 6) -> int:
        """Roll a single die with the given number of faces"""
        return random.randint(1, faces)
        
    def roll_dice(self, num_dice: int, faces: int = 6) -> List[int]:
        """Roll multiple dice with the given number of faces"""
        return [self.roll_die(faces) for _ in range(num_dice)]
    
    def simulate_rolls(self, num_rolls: int, num_dice: int, faces: int = 6) -> List[List[int]]:
        """Simulate multiple rolls of multiple dice"""
        return [self.roll_dice(num_dice, faces) for _ in range(num_rolls)]
    
    def calculate_statistics(self, rolls: List[int]) -> Tuple[Dict[int, int], int, Dict[int, float]]:
        """Calculate statistics for single die rolls"""
        counts = Counter(rolls)
        total = len(rolls)
        percentages = {face: (count / total * 100) if total > 0 else 0.0 
                      for face, count in counts.items()}
        return counts, total, percentages
    
    def calculate_multi_statistics(self, rolls: List[List[int]], dice_faces: int) -> Tuple[Dict[int, int], int, Dict[int, float], Dict[int, Dict[int, int]]]:
        """Calculate statistics for multiple dice rolls"""
        # Flatten all rolls to get overall distribution
        all_values = [v for roll in rolls for v in roll]
        counts = Counter(all_values)
        total = len(all_values)
        percentages = {face: (counts.get(face, 0) / total * 100) if total > 0 else 0.0 
                      for face in range(1, dice_faces + 1)}
        
        # Calculate per-position statistics
        position_stats = {}
        if rolls and all(len(roll) == len(rolls[0]) for roll in rolls):
            num_positions = len(rolls[0])
            for pos in range(num_positions):
                position_values = [roll[pos] for roll in rolls if len(roll) > pos]
                position_stats[pos] = Counter(position_values)
                
        return counts, total, percentages, position_stats
    
    def set_current_dice(self, dice_set: str, num_dice: int, faces: int):
        """Set the current dice configuration"""
        self.current_dice_set = dice_set
        self.current_num_dice = num_dice
        self.current_dice_faces = faces
        self.current_roll = []
