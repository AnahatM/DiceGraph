import os
from datetime import datetime
from pathlib import Path

# Constants for file paths
SINGLE_DICE_DIR = "SingleDiceResults"
MULTIPLE_DICE_DIR = "MultipleDiceResults"

def ensure_directories():
    """Ensure that the necessary directories exist"""
    os.makedirs(SINGLE_DICE_DIR, exist_ok=True)
    os.makedirs(MULTIPLE_DICE_DIR, exist_ok=True)

def get_file_path(dice_name, num_dice=1):
    """Get the file path for a given dice name and number of dice"""
    # Remove any invalid characters for filenames
    safe_name = "".join(c for c in dice_name if c.isalnum() or c in " _-").strip()
    safe_name = safe_name.replace(" ", "_")
    
    if num_dice == 1:
        directory = SINGLE_DICE_DIR
    else:
        directory = MULTIPLE_DICE_DIR
        
    return os.path.join(directory, f"{safe_name}.txt")

def log_single_roll(file_path, value):
    """Log a single dice roll to the specified file"""
    with open(file_path, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {value}\n")

def log_multiple_rolls(file_path, values):
    """Log multiple dice rolls to the specified file"""
    with open(file_path, 'a') as f:
        f.write(f"{','.join(map(str, values))}\n")

def read_single_rolls(file_path):
    """Read single dice rolls from a file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        rolls = [int(line.strip().split('-')[-1]) for line in lines 
                if line.strip() and line.strip().split('-')[-1].strip().isdigit()]
        return rolls
    except FileNotFoundError:
        return []

def read_multiple_rolls(file_path):
    """Read multiple dice rolls from a file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        rolls = [list(map(int, line.strip().split(','))) for line in lines if line.strip()]
        return rolls
    except FileNotFoundError:
        return []

def reset_file(file_path):
    """Reset the contents of a file"""
    with open(file_path, 'w') as f:
        pass

def get_available_dice_sets(directory):
    """Get a list of available dice sets from a directory"""
    if not os.path.exists(directory):
        return []
    
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    return [os.path.splitext(f)[0] for f in files]
