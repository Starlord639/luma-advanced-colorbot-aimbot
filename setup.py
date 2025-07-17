#!/usr/bin/env python3
"""
Luma Aimbot Setup Script
Installs dependencies and sets up the environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False
    return True

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required!")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_config():
    """Create default configuration file"""
    config_content = """{
  "target_color": [255, 0, 0],
  "tolerance": 10,
  "sensitivity": 1.0,
  "reaction_speed": 0.1,
  "scan_area": [0, 0, 1920, 1080],
  "hotkey": "F8",
  "auto_start": false
}"""
    
    if not os.path.exists("luma_config.json"):
        with open("luma_config.json", "w") as f:
            f.write(config_content)
        print("✓ Default configuration created")
    else:
        print("✓ Configuration file already exists")

def main():
    """Main setup function"""
    print("=" * 50)
    print("    Luma Aimbot Setup")
    print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    if not install_requirements():
        sys.exit(1)
    
    create_config()
    
    print("\n" + "=" * 50)
    print("    Setup Complete!")
    print("=" * 50)
    print("\nTo run Luma Aimbot:")
    print("  python luma_aimbot.py")
    print("\nHotkeys:")
    print("  F8 - Toggle aimbot on/off")
    print("\nGUI will open automatically in your browser")
    print("Default URL: http://localhost:5000")

if __name__ == "__main__":
    main()
