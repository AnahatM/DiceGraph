import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Constants for file paths
SINGLE_DICE_DIR = "SingleDiceResults"
MULTIPLE_DICE_DIR = "MultipleDiceResults"
SIMULATION_DIR = "SimulationResults"
FILE_EXTENSION = "dicegraph"  # Using .dicegraph extension for all data files

def ensure_directories():
    """Ensure that the necessary directories exist"""
    os.makedirs(SINGLE_DICE_DIR, exist_ok=True)
    os.makedirs(MULTIPLE_DICE_DIR, exist_ok=True)
    os.makedirs(SIMULATION_DIR, exist_ok=True)

def get_file_path(dice_name, num_dice=1):
    """Get the file path for a given dice name and number of dice"""
    # Remove any invalid characters for filenames
    safe_name = "".join(c for c in dice_name if c.isalnum() or c in " _-").strip()
    safe_name = safe_name.replace(" ", "_")
    
    if num_dice == 1:
        directory = SINGLE_DICE_DIR
    else:
        directory = MULTIPLE_DICE_DIR
        
    return os.path.join(directory, f"{safe_name}.{FILE_EXTENSION}")

def get_simulation_file_path(dice_name, num_dice, faces, num_rolls):
    """
    Get the file path for a simulation with the given parameters.
    Format: {num_dice}dice_{faces}faces_{num_rolls}rolls_{name}.dicegraph
    """
    # Remove any invalid characters for filenames
    safe_name = "".join(c for c in dice_name if c.isalnum() or c in " _-").strip()
    safe_name = safe_name.replace(" ", "_")
    
    # Create formatted filename with parameters as requested
    filename = f"{num_dice}dice_{faces}faces_{num_rolls}rolls_{safe_name}.{FILE_EXTENSION}"
    return os.path.join(SIMULATION_DIR, filename)

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

def delete_file(file_path):
    """Delete a file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_available_dice_sets(directory):
    """Get a list of available dice sets from a directory"""
    if not os.path.exists(directory):
        return []
    
    files = [f for f in os.listdir(directory) if f.endswith(f'.{FILE_EXTENSION}')]
    return [os.path.splitext(f)[0] for f in files]

def get_available_simulations():
    """Get a list of available simulation files"""
    if not os.path.exists(SIMULATION_DIR):
        return []
    
    files = [f for f in os.listdir(SIMULATION_DIR) if f.endswith(f'.{FILE_EXTENSION}')]
    
    # Parse simulation filenames to get information
    simulations = []
    for file in files:
        name = os.path.splitext(file)[0]
        parts = name.split('_')
        
        if len(parts) >= 4:
            try:
                num_dice = int(parts[0].replace('dice', ''))
                faces = int(parts[1].replace('faces', ''))
                num_rolls = int(parts[2].replace('rolls', ''))
                sim_name = '_'.join(parts[3:])
                
                simulations.append({
                    'filename': file,
                    'name': sim_name,
                    'num_dice': num_dice,
                    'faces': faces,
                    'num_rolls': num_rolls,
                    'full_path': os.path.join(SIMULATION_DIR, file)
                })
            except (ValueError, IndexError):
                # Skip files that don't match the expected format
                pass
                
    return simulations

def parse_simulation_filename(filename):
    """Parse a simulation filename to extract parameters"""
    try:
        # Remove extension
        name = os.path.splitext(filename)[0]
        parts = name.split('_')
        
        num_dice = int(parts[0].replace('dice', ''))
        faces = int(parts[1].replace('faces', ''))
        num_rolls = int(parts[2].replace('rolls', ''))
        sim_name = '_'.join(parts[3:])
        
        return {
            'name': sim_name,
            'num_dice': num_dice,
            'faces': faces,
            'num_rolls': num_rolls
        }
    except (ValueError, IndexError):
        return None
