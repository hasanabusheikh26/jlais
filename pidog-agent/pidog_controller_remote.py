"""
Remote PiDog Controller - Connects to hardware server via HTTP
Works from any machine (Mac, cloud, etc.)
"""

import logging
import requests
import cv2
import numpy as np
from typing import Optional

logger = logging.getLogger("pidog-controller-remote")


class PiDogControllerRemote:
    """
    Remote controller for PiDog hardware via HTTP API.
    
    The hardware server runs on the Pi, this controller runs anywhere.
    """
    
    def __init__(self, pi_host: str = "raspberrypi.local", pi_port: int = 5000):
        """
        Args:
            pi_host: Hostname or IP of Raspberry Pi (e.g., "192.168.1.100")
            pi_port: Port number of hardware server (default: 5000)
        """
        self.base_url = f"http://{pi_host}:{pi_port}"
        self.mode = "remote"
        
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.ok:
                data = response.json()
                logger.info(f"✅ Connected to Pi at {pi_host}:{pi_port}")
                logger.info(f"   Hardware available: {data.get('hardware_available')}")
            else:
                logger.warning(f"⚠️  Pi responded but unhealthy: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to Pi at {pi_host}:{pi_port}")
            logger.error(f"   Error: {e}")
            logger.error(f"   Make sure pidog_hardware_server.py is running on Pi!")
    
    def get_camera_frame(self) -> Optional[np.ndarray]:
        """
        Get current camera frame from Pi.
        
        Returns:
            numpy.ndarray: BGR image frame
        """
        try:
            response = requests.get(f"{self.base_url}/camera/frame", timeout=1)
            if response.ok:
                # Decode JPEG to numpy array
                img_array = np.frombuffer(response.content, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                return frame
        except Exception as e:
            logger.error(f"Camera frame error: {e}")
        
        # Return black frame on error
        return np.zeros((720, 1280, 3), dtype=np.uint8)
    
    def perform_action(self, action_name: str, **kwargs) -> dict:
        """
        Execute a PiDog physical action on the Pi.
        
        Args:
            action_name: Action name (sit, bark, wag_tail, etc.)
            **kwargs: Optional parameters (speed, steps, etc.)
        
        Returns:
            dict: Result with success status
        """
        try:
            response = requests.post(
                f"{self.base_url}/action/{action_name}",
                json=kwargs,
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                logger.info(f"✅ Remote action '{action_name}' executed")
                return result
            else:
                logger.error(f"❌ Action '{action_name}' failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        
        except Exception as e:
            logger.error(f"❌ Action '{action_name}' failed: {e}")
            return {"success": False, "error": str(e)}
    
    def shutdown(self):
        """Clean shutdown of hardware on Pi"""
        try:
            response = requests.post(f"{self.base_url}/shutdown", timeout=2)
            if response.ok:
                logger.info("✅ Pi hardware shutdown")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
