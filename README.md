# DiceGraph

A comprehensive tool for tracking, analyzing, and simulating dice rolls. Use this application to check if your dice are fair, visualize roll distributions, and simulate large numbers of dice rolls.

## Features

- **Dice Tracking**: Track rolls for single or multiple dice
- **Custom Dice Support**: Support for dice with any number of faces (d3, d4, d6, d8, d10, d12, d20, d100, etc.)
- **Named Dice Sets**: Save and organize dice sets with custom names
- **Roll Simulation**: Simulate large numbers of rolls quickly
- **Data Visualization**: View distributions and statistics for your dice rolls
- **Data Management**: Save, load, and reset dice roll data

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone this repository:
   ```
   git clone https://github.com/yourusername/DiceGraph.git
   cd DiceGraph
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main application:

```
python main.py
```

### Dice Roller Tab

1. Set the number of dice, number of faces, and give your dice set a name
2. Click "Apply" to configure the dice set
3. Roll dice by clicking on the numbered buttons
4. View the distribution graph that updates after each roll
5. Use "Reset Data" to clear all rolls for the current dice set
6. Use "Load Set" to select from previously saved dice sets

### Dice Simulator Tab

1. Configure the simulation parameters (number of dice, faces, and rolls)
2. Give your simulation a name
3. Click "Run Simulation" to generate and visualize the results
4. The simulation data is automatically saved and can be loaded in the Dice Roller tab

## File Structure

- `main.py`: Application entry point
- `gui.py`: User interface components
- `dice_manager.py`: Core dice functionality
- `file_utils.py`: File operations for saving/loading dice data
- `simulation.py`: Dice simulation functionality
- `SingleDiceResults/`: Directory for single dice roll data files
- `MultipleDiceResults/`: Directory for multiple dice roll data files
