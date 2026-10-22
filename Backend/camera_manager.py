"""
RiskVision 2.0 - Dual-Camera Stream Manager
Handles concurrent, multi-threaded frame acquisition for:
- Camera 1: Laptop USB Webcam (Default 0)
- Camera 2: Remote ESP32-CAM (Wi-Fi stream) / Secondary Camera / Loopback Video fallback
"""

import cv2
import threading
import time
import os

class VideoCaptureThread:
    """Thread-safe, non-blocking camera frame grabber."""
    def __init__(self, src, name="Camera", width=1280, height=720):
        self.src = src
        self.name = name
        self.width = width
        self.height = height
        
        self.cap = None
        self.frame = None
        self.is_opened = False
        self.running = False
        self.lock = threading.Lock()
        self.fps = 30.0
        self.last_frame_time = 0.0

    def start(self):
        if self.running:
            return self
            
        print(f"[{self.name}] Connecting to source: {self.src}")
        try:
            # Check if source is integer (local camera)
            if isinstance(self.src, str) and self.src.isdigit():
                self.src = int(self.src)
                
            self.cap = cv2.VideoCapture(self.src)
            if isinstance(self.src, int):
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
                if actual_fps and actual_fps > 0:
                    self.fps = actual_fps
                    
            self.is_opened = self.cap.isOpened()
        except Exception as e:
            print(f"[{self.name}] Initialization error: {e}")
            self.is_opened = False

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return self

    def _capture_loop(self):
        retry_delay = 2.0
        while self.running:
            if not self.is_opened or self.cap is None or not self.cap.isOpened():
                time.sleep(retry_delay)
                try:
                    self.cap = cv2.VideoCapture(self.src)
                    self.is_opened = self.cap.isOpened()
                    if self.is_opened:
                        print(f"[{self.name}] Successfully reconnected.")
                except Exception:
                    continue
                    
            success, frame = self.cap.read()
            if success and frame is not None:
                with self.lock:
                    self.frame = frame
                    self.last_frame_time = time.time()
            else:
                # If reading from a video file fallback, loop back to start
                if isinstance(self.src, str) and os.path.exists(self.src):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                time.sleep(0.01)

    def read(self):
        with self.lock:
            if self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        self.is_opened = False
        print(f"[{self.name}] Stopped.")

class DualCameraManager:
    """Manages Camera 1 and Camera 2 streams concurrently."""
    def __init__(self, cam1_src=0, cam2_src=None):
        self.cam1_src = cam1_src
        
        # If cam2_src is not provided, look for ESP32_CAM_URL in env or fallback to local sample video
        if cam2_src is None:
            cam2_src = os.getenv("ESP32_CAM_URL", "")
            if not cam2_src:
                fallback_video = os.path.abspath("test_mp4v.mp4")
                if os.path.exists(fallback_video):
                    cam2_src = fallback_video
                else:
                    cam2_src = 1 # Try secondary camera or index 1
                    
        self.cam2_src = cam2_src
        self.cam1 = VideoCaptureThread(self.cam1_src, name="Camera-1 (Webcam)")
        self.cam2 = VideoCaptureThread(self.cam2_src, name="Camera-2 (ESP32-CAM / Node 2)")

    def start(self):
        self.cam1.start()
        self.cam2.start()

    def stop(self):
        self.cam1.stop()
        self.cam2.stop()

    def set_cam2_source(self, new_src):
        """Allows dynamically updating Camera 2 URL (e.g. after ESP32 connects to Wi-Fi)."""
        print(f"[DualCameraManager] Switching Camera 2 source to: {new_src}")
        self.cam2.stop()
        self.cam2_src = new_src
        self.cam2 = VideoCaptureThread(self.cam2_src, name="Camera-2 (ESP32-CAM)")
        self.cam2.start()

    def get_cam1_frame(self):
        return self.cam1.read()

    def get_cam2_frame(self):
        return self.cam2.read()

# Global singleton instance
camera_manager = DualCameraManager()

if __name__ == "__main__":
    print("Testing DualCameraManager...")
    camera_manager.start()
    time.sleep(1.0)
    
    s1, f1 = camera_manager.get_cam1_frame()
    print(f"Camera 1 status: {s1} | Frame shape: {f1.shape if s1 else None}")
    
    s2, f2 = camera_manager.get_cam2_frame()
    print(f"Camera 2 status: {s2} | Frame shape: {f2.shape if s2 else None}")
    
    camera_manager.stop()
    print("Camera Manager test complete.")
