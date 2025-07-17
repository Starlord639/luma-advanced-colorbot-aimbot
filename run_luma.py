#!/usr/bin/env python3
"""
Luma Aimbot Launcher
Quick launch script with system checks
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'cv2', 'numpy', 'pyautogui', 'flask', 
        'flask_cors', 'keyboard', 'screeninfo'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nRun 'python setup.py' to install dependencies")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_permissions():
    """Check system permissions"""
    try:
        import pyautogui
        # Test mouse control
        current_pos = pyautogui.position()
        print(f"✅ Mouse control available at {current_pos}")
        return True
    except Exception as e:
        print(f"❌ Mouse control error: {e}")
        print("   Try running as administrator or check accessibility permissions")
        return False

def launch_application():
    """Launch the main application"""
    try:
        print("🚀 Starting Luma Aimbot...")
        print("   GUI will open in your browser")
        print("   Press F8 to toggle aimbot")
        print("   Press Ctrl+C to exit")
        print("-" * 50)
        
        # Import and run the main application
        from luma_aimbot import main
        main()
        
    except KeyboardInterrupt:
        print("\n👋 Luma Aimbot stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 50)
    print("    🎯 Luma Aimbot Launcher")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're in the right directory
    if not Path("luma_aimbot.py").exists():
        print("❌ luma_aimbot.py not found!")
        print("   Make sure you're in the correct directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check permissions
    if not check_permissions():
        print("⚠️  Continuing anyway, but functionality may be limited")
    
    # Launch application
    launch_application()

if __name__ == "__main__":
    main()
