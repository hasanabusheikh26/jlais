#!/usr/bin/env python3
"""
PiDog Hardware Server - Runs on Raspberry Pi
Exposes HTTP API for controlling PiDog hardware remotely
"""

from flask import Flask, jsonify, request, Response
import logging
import time

# Try to import hardware
try:
    from pidog import Pidog
    from vilib import Vilib
    import cv2
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pidog-hardware-server")

# Global hardware instances
dog = None
camera_active = False

def init_hardware():
    """Initialize PiDog hardware"""
    global dog, camera_active
    
    if not HARDWARE_AVAILABLE:
        logger.warning("Hardware not available - mock mode")
        return
    
    try:
        dog = Pidog()
        time.sleep(0.5)
        
        # Initialize camera
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.display(local=False, web=False)
        camera_active = True
        
        # Initial position
        dog.do_action("stand", speed=80)
        time.sleep(1)
        
        logger.info("✅ PiDog hardware initialized")
    except Exception as e:
        logger.error(f"Hardware init failed: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "hardware_available": HARDWARE_AVAILABLE,
        "camera_active": camera_active
    })

@app.route('/action/<action_name>', methods=['POST'])
def perform_action(action_name):
    """Execute a PiDog action"""
    data = request.get_json() or {}
    speed = data.get('speed', 80)
    steps = data.get('steps', 3)
    
    if not HARDWARE_AVAILABLE:
        logger.info(f"MOCK: {action_name} (speed={speed})")
        return jsonify({"success": True, "action": action_name, "mock": True})
    
    try:
        if action_name in ["forward", "backward", "turn_left", "turn_right"]:
            dog.do_action(action_name, step_count=steps, speed=speed)
        else:
            dog.do_action(action_name, speed=speed)
        
        time.sleep(0.5)
        logger.info(f"✅ Action: {action_name}")
        return jsonify({"success": True, "action": action_name})
    
    except Exception as e:
        logger.error(f"Action failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/camera/frame', methods=['GET'])
def get_camera_frame():
    """Get current camera frame as JPEG"""
    if not HARDWARE_AVAILABLE or not camera_active:
        # Return mock frame
        import numpy as np
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(mock_frame, "MOCK CAMERA", (200, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', mock_frame)
        return Response(buffer.tobytes(), mimetype='image/jpeg')
    
    try:
        frame = Vilib.img
        if frame is not None:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return Response(buffer.tobytes(), mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Camera error: {e}")
    
    return jsonify({"error": "Camera unavailable"}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown hardware cleanly"""
    if HARDWARE_AVAILABLE and dog:
        try:
            dog.do_action("sit", speed=50)
            time.sleep(1)
            Vilib.camera_close()
            logger.info("✅ Hardware shutdown")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    return jsonify({"success": True})

if __name__ == '__main__':
    init_hardware()
    
    # Run server
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=False
    )
