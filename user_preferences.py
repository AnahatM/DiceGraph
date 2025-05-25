"""
User preferences management for DiceGraph application.
Handles saving and loading user preferences from a JSON file.
"""

import os
import json
from typing import Dict, Any, Optional

# Preferences file
PREFERENCES_FILE = "usersettings.dicegraphprefs"

# Default preferences
DEFAULT_PREFERENCES = {
    "dark_mode": False,
    "default_faces": 6,
    "window_width": 800,
    "window_height": 600,
    "statistical_alpha": 0.05
}

def load_preferences() -> Dict[str, Any]:
    """
    Load user preferences from the JSON file.
    If the file doesn't exist, returns default preferences.
    """
    try:
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, 'r') as f:
                prefs = json.load(f)
            # Ensure all default keys exist
            for key, value in DEFAULT_PREFERENCES.items():
                if key not in prefs:
                    prefs[key] = value
            return prefs
        else:
            return DEFAULT_PREFERENCES.copy()
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return DEFAULT_PREFERENCES.copy()

def save_preferences(preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to the JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False

def get_preference(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a specific preference value.
    If the preference doesn't exist, returns the provided default or None.
    """
    prefs = load_preferences()
    return prefs.get(key, default)

def set_preference(key: str, value: Any) -> bool:
    """
    Set a specific preference value and save it.
    Returns True if successful, False otherwise.
    """
    prefs = load_preferences()
    prefs[key] = value
    return save_preferences(prefs)
