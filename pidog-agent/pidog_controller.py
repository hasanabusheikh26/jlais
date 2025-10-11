import logging
import time
import cv2
import numpy as np

logger = logging.getLogger("pidog-controller")

# Try to import PiDog hardware - gracefully fail if not on Pi
try:
    from pidog import Pidog
    from vilib import Vilib
    HARDWARE_AVAILABLE = True
    logger.info("✅ PiDog hardware libraries loaded")
except ImportError:
    HARDWARE_AVAILABLE = False
    logger.warning("⚠️  PiDog hardware not available - using mock mode for testing")


class PiDogController:
    """
    Hardware abstraction layer for SunFounder PiDog robot.
    
    Features:
    - Automatically detects hardware availability
    - Uses mock mode when not on Raspberry Pi (for local testing)
    - Real hardware mode when PiDog libraries are available
    """
    
    def __init__(self):
        if HARDWARE_AVAILABLE:
            logger.info("🔧 Initializing REAL PiDog hardware...")
            self.dog = Pidog()
            time.sleep(0.5)
            
            # Initialize camera
            Vilib.camera_start(vflip=False, hflip=False)
            Vilib.display(local=False, web=False)
            
            # Set initial position
            self.dog.do_action("stand", speed=80)
            time.sleep(1)
            
            logger.info("✅ PiDog hardware initialized")
            self.mode = "hardware"
        else:
            logger.info("🎭 Using MOCK PiDog (testing mode - no hardware)")
            self.dog = None
            self.mode = "mock"
    
    def get_camera_frame(self):
        """
        Get current camera frame.
        
        Returns:
            numpy.ndarray: BGR image frame (1280x720)
        """
        if HARDWARE_AVAILABLE:
            try:
                frame = Vilib.img
                if frame is not None:
                    # Convert RGB to BGR for OpenCV compatibility
                    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception as e:
                logger.error(f"Camera error: {e}")
        
        # Return mock frame (for testing without hardware)
        mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.putText(mock_frame, "MOCK PIDOG CAMERA", (350, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        cv2.putText(mock_frame, "Hardware will stream real video", (350, 420),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return mock_frame
    
    def perform_action(self, action_name: str, **kwargs):
        """
        Execute a PiDog physical action.
        
        Args:
            action_name: Action name (sit, bark, wag_tail, etc.)
            **kwargs: Optional parameters (speed, steps, etc.)
        
        Returns:
            dict: Result with success status
        """
        speed = kwargs.get("speed", 80)
        
        if HARDWARE_AVAILABLE:
            try:
                logger.info(f"🎬 Executing: {action_name} (speed={speed})")
                
                # Handle movement actions with step count
                if action_name in ["forward", "backward", "turn_left", "turn_right"]:
                    steps = kwargs.get("steps", 3)
                    self.dog.do_action(action_name, step_count=steps, speed=speed)
                else:
                    # Standard actions
                    self.dog.do_action(action_name, speed=speed)
                
                time.sleep(0.5)  # Let action complete
                logger.info(f"✅ Action '{action_name}' completed")
                return {"success": True, "action": action_name}
                
            except Exception as e:
                logger.error(f"❌ Action '{action_name}' failed: {e}")
                return {"success": False, "action": action_name, "error": str(e)}
        else:
            # Mock mode - log what would happen
            logger.info(f"🎭 MOCK: Would execute '{action_name}' (speed={speed})")
            return {"success": True, "action": action_name, "mock": True}
    
    def shutdown(self):
        """Clean shutdown of hardware"""
        if HARDWARE_AVAILABLE:
            try:
                logger.info("🛑 Shutting down PiDog hardware...")
                self.dog.do_action("sit", speed=50)
                time.sleep(1)
                Vilib.camera_close()
                logger.info("✅ PiDog shutdown complete")
            except Exception as e:
                logger.error(f"Shutdown error: {e}")
        else:
            logger.info("🎭 MOCK shutdown complete")
