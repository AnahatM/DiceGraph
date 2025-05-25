"""
Test file specifically for reset button functionality in the simulation tab.
"""
import tkinter as tk
import os
from gui import DiceTrackerApp

def main():
    """Test the reset button functionality"""
    print("Testing reset button functionality...")
    
    # SimulationResults directory should exist
    sim_dir = "SimulationResults"
    if os.path.exists(sim_dir) and os.path.isdir(sim_dir):
        print(f"✅ SimulationResults directory exists")
    else:
        print(f"❌ SimulationResults directory not found")
    
    # Check if reset button exists in DiceSimulatorTab
    try:
        root = tk.Tk()
        app = DiceTrackerApp(root)
        app.setup_ui()
        
        # Check if reset_simulation method exists
        if hasattr(app.simulator_tab, 'reset_simulation'):
            print("✅ Reset simulation method exists")
        else:
            print("❌ Reset simulation method not found")
        
        # Check if the button exists in the UI
        reset_buttons = [widget for widget in app.simulator_tab.parent.winfo_children() 
                        if hasattr(widget, 'cget') and 
                        'text' in widget.keys() and 
                        widget.cget('text') == "Reset"]
        
        if reset_buttons:
            print("✅ Reset button found in the simulator tab UI")
        else:
            # Check in subframes
            found = False
            for widget in app.simulator_tab.parent.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if (hasattr(child, 'winfo_children')):
                            for subchild in child.winfo_children():
                                if (hasattr(subchild, 'cget') and 
                                    'text' in subchild.keys() and 
                                    subchild.cget('text') == "Reset"):
                                    found = True
            
            if found:
                print("✅ Reset button found in the simulator tab UI (in subframe)")
            else:
                print("❌ Reset button not found in the simulator tab UI")
                
        root.destroy()
    except Exception as e:
        print(f"❌ Error testing reset button: {e}")
    
    print("\nReset button testing complete!")

if __name__ == "__main__":
    main()
