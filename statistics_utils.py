"""
Statistics utility functions for DiceGraph application.
Provides functions for statistical analysis of dice rolls.
"""

import numpy as np
from typing import List, Dict, Tuple, Union, Optional
from scipy import stats
import scipy.stats as stats
from collections import Counter

def chi_square_test(observed: List[int], expected_probs: Optional[List[float]] = None) -> Tuple[float, float]:
    """
    Perform a chi-square goodness of fit test to check if dice rolls are fair.
    
    Args:
        observed: List of observed frequencies (counts of each face)
        expected_probs: List of expected probabilities, if None assumes uniform distribution
        
    Returns:
        Tuple of (test statistic, p-value)
    """
    total = sum(observed)
    if total == 0:
        return 0, 1.0
        
    # If expected_probs is None, assume uniform distribution
    num_categories = len(observed)
    if expected_probs is None:
        expected_probs = [1/num_categories] * num_categories
    
    # Calculate expected frequencies
    expected = [total * p for p in expected_probs]
    
    # Perform chi-square test
    try:
        test_stat, p_value = stats.chisquare(observed, expected)
        return test_stat, p_value
    except Exception:
        # If test fails (e.g., due to zero expected values)
        return 0, 1.0

def interpret_chi_square_result(p_value: float, alpha: float = 0.05) -> Dict[str, Union[str, float]]:
    """
    Interpret the results of a chi-square test.
    
    Args:
        p_value: The p-value from the chi-square test
        alpha: The significance level (default: 0.05)
        
    Returns:
        Dictionary with interpretation and data
    """
    result = {
        "p_value": p_value,
        "alpha": alpha,
        "is_fair": p_value >= alpha,
        "conclusion": "",
        "confidence_level": (1 - alpha) * 100
    }
    
    if p_value >= alpha:
        result["conclusion"] = f"The dice appear to be fair (p={p_value:.3f} ≥ α={alpha:.3f})"
        result["significance"] = f"No significant deviation from fairness at {(1-alpha)*100:.1f}% confidence level"
    else:
        result["conclusion"] = f"The dice may not be fair (p={p_value:.3f} < α={alpha:.3f})"
        result["significance"] = f"Statistically significant deviation from fairness at {(1-alpha)*100:.1f}% confidence level"
    
    return result

def get_dice_fairness(rolls: List[Union[int, List[int]]], num_faces: int, alpha: float = 0.05) -> Dict[str, Union[str, float, Dict]]:
    """
    Analyze dice rolls for fairness.
    
    Args:
        rolls: List of rolls (either single values or lists for multiple dice)
        num_faces: Number of faces on the dice
        alpha: Significance level for statistical tests
        
    Returns:
        Dictionary with fairness analysis results
    """
    # Flatten the rolls if they're in lists
    if rolls and isinstance(rolls[0], list):
        flat_rolls = [val for roll in rolls for val in roll]
    else:
        flat_rolls = rolls
    
    # Count occurrences of each face
    counts = Counter(flat_rolls)
    observed = [counts.get(i, 0) for i in range(1, num_faces + 1)]
    
    # Perform chi-square test
    chi2_stat, p_value = chi_square_test(observed)
    
    # Interpret results
    fairness = interpret_chi_square_result(p_value, alpha)
    fairness['chi2_stat'] = chi2_stat
    
    # Add additional stats
    total_rolls = len(flat_rolls)
    face_percentages = {i: (counts.get(i, 0) / total_rolls * 100 if total_rolls > 0 else 0) 
                       for i in range(1, num_faces + 1)}
    
    return {
        "fairness_test": fairness,
        "total_rolls": total_rolls,
        "face_counts": counts,
        "face_percentages": face_percentages,
    }
