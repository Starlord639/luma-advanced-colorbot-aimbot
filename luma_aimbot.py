#!/usr/bin/env python3
"""
Luma - Advanced ColorBot Aimbot
A sophisticated screen scanning aimbot with smooth mouse movement and customizable settings
"""

import cv2
import numpy as np
import pyautogui
import threading
import time
import json
import os
from datetime import datetime
import logging
from typing import Tuple, Optional, Dict, Any
import keyboard
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
import webbrowser
from screeninfo import get_monitors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LumaAimbot')

class ColorDetector:
    """Advanced color detection with HSV color space for better accuracy"""
    
    def __init__(self, target_color: Tuple[int, int, int], tolerance: int = 10):
        self.target_color = target_color
        self.tolerance = tolerance
        self.lower_bound = None
        self.upper_bound = None
        self.update_bounds()
        
    def update_bounds(self):
        """Update HSV bounds based on target color and tolerance"""
        hsv_color = cv2.cvtColor(np.uint8([[self.target_color]]), cv2.COLOR_BGR2HSV)[0][0]
        
        # Handle hue wraparound
        lower_h = max(0, hsv_color[0] - self.tolerance)
        upper_h = min(179, hsv_color[0] + self.tolerance)
        
        lower_s = max(0, hsv_color[1] - 50)
        upper_s = min(255, hsv_color[1] + 50)
        
        lower_v = max(0, hsv_color[2] - 50)
        upper_v = min(255, hsv_color[2] + 50)
        
        self.lower_bound = np.array([lower_h, lower_s, lower_v])
        self.upper_bound = np.array([upper_h, upper_s, upper_v])
    
    def detect_color(self, screenshot: np.ndarray) -> Optional[Tuple[int, int]]:
        """Detect target color in screenshot and return center coordinates"""
        try:
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
            
            # Apply morphological operations to reduce noise
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate center using moments
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                return (center_x, center_y)
                
        except Exception as e:
            logger.error(f"Error in color detection: {e}")
            
        return None

class SmoothMouse:
    """Smooth mouse movement with adjustable speed and acceleration"""
    
    def __init__(self, sensitivity: float = 1.0, reaction_speed: float = 0.1):
        self.sensitivity = sensitivity
        self.reaction_speed = reaction_speed
        self.current_x, self.current_y = pyautogui.position()
        
    def move_to(self, target_x: int, target_y: int):
        """Move mouse smoothly to target position"""
        try:
            # Calculate distance
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            distance = np.sqrt(dx**2 + dy**2)
            
            if distance < 5:  # Skip small movements
                return
                
            # Calculate steps based on distance and reaction speed
            steps = max(1, int(distance * self.reaction_speed))
            
            for i in range(steps):
                progress = (i + 1) / steps
                # Apply easing function for smoother movement
                eased_progress = self.ease_in_out_cubic(progress)
                
                new_x = int(self.current_x + dx * eased_progress * self.sensitivity)
                new_y = int(self.current_y + dy * eased_progress * self.sensitivity)
                
                pyautogui.moveTo(new_x, new_y)
                self.current_x, self.current_y = new_x, new_y
                
                # Small delay for smooth movement
                time.sleep(0.001)
                
        except Exception as e:
            logger.error(f"Error moving mouse: {e}")
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic easing function for smooth transitions"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

class LumaAimbot:
    """Main aimbot class with configuration and control"""
    
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        self.paused = False
        self.detector = None
        self.mouse = None
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Get actual screen dimensions
        try:
            monitors = get_monitors()
            if monitors:
                self.screen_width = monitors[0].width
                self.screen_height = monitors[0].height
        except:
            pass
            
        self.update_detector()
        self.update_mouse()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = "luma_config.json"
        default_config = {
            "target_color": [255, 0, 0],  # Red by default
            "tolerance": 10,
            "sensitivity": 1.0,
            "reaction_speed": 0.1,
            "scan_area": [0, 0, 1920, 1080],  # Full screen
            "hotkey": "F8",
            "auto_start": False
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open("luma_config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def update_detector(self):
        """Update color detector with current settings"""
        color = tuple(self.config["target_color"])
        tolerance = self.config["tolerance"]
        self.detector = ColorDetector(color, tolerance)
    
    def update_mouse(self):
        """Update mouse settings"""
        sensitivity = self.config["sensitivity"]
        reaction_speed = self.config["reaction_speed"]
        self.mouse = SmoothMouse(sensitivity, reaction_speed)
    
    def scan_screen(self) -> Optional[Tuple[int, int]]:
        """Scan screen for target color"""
        try:
            x, y, w, h = self.config["scan_area"]
            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            center = self.detector.detect_color(frame)
            if center:
                return (center[0] + x, center[1] + y)
                
        except Exception as e:
            logger.error(f"Error scanning screen: {e}")
            
        return None
    
    def aimbot_loop(self):
        """Main aimbot loop"""
        logger.info("Aimbot started")
        
        while self.running:
            if not self.paused:
                target_pos = self.scan_screen()
                if target_pos:
                    self.mouse.move_to(target_pos[0], target_pos[1])
            
            time.sleep(0.01)  # 100 FPS
            
        logger.info("Aimbot stopped")
    
    def start(self):
        """Start the aimbot"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.aimbot_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the aimbot"""
        self.running = False
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        logger.info(f"Aimbot {'paused' if self.paused else 'resumed'}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration and save"""
        self.config.update(new_config)
        self.update_detector()
        self.update_mouse()
        self.save_config()

# Flask API for GUI communication
app = Flask(__name__, template_folder='templates')
CORS(app)
aimbot = LumaAimbot()

@app.route('/')
def index():
    """Serve the main GUI"""
    from flask import render_template
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current aimbot status"""
    return jsonify({
        'running': aimbot.running,
        'paused': aimbot.paused,
        'config': aimbot.config
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update aimbot configuration"""
    try:
        new_config = request.json
        aimbot.update_config(new_config)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/start', methods=['POST'])
def start_aimbot():
    """Start the aimbot"""
    try:
        aimbot.start()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stop', methods=['POST'])
def stop_aimbot():
    """Stop the aimbot"""
    try:
        aimbot.stop()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/toggle', methods=['POST'])
def toggle_aimbot():
    """Toggle aimbot pause state"""
    try:
        aimbot.toggle_pause()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def setup_hotkeys():
    """Setup keyboard hotkeys"""
    keyboard.add_hotkey('F8', aimbot.toggle_pause)
    
def main():
    """Main entry point"""
    # Setup hotkeys
    setup_hotkeys()
    
    # Start Flask server
    port = 5000
    webbrowser.open(f'http://localhost:{port}')
    
    logger.info("Starting Luma Aimbot...")
    logger.info(f"GUI available at http://localhost:{port}")
    logger.info("Press F8 to toggle aimbot")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
