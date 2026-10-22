"""
RiskVision 2.0 - IoT Gateway & Telemetry Hub
Manages PIR motion sensor gating and active deterrence buzzer commands.
Supports both HTTP REST webhooks and optional MQTT connectivity.
"""

import time
import threading

class IoTHub:
    def __init__(self):
        # PIR Motion Sensor State
        self.pir_enabled = True
        self.motion_detected = True       # Defaults to True so inference works out-of-the-box
        self.last_motion_time = time.time()
        self.motion_timeout_seconds = 15.0 # Sleep after 15s of zero motion
        
        # Actuator State
        self.buzzer_state = False
        self.last_buzzer_trigger = 0.0
        
        # ESP32-CAM Node Status
        self.esp32_ip = None
        self.esp32_last_heartbeat = 0.0

    def update_pir_motion(self, detected=True):
        """Called when PIR sensor detects motion."""
        self.motion_detected = bool(detected)
        if self.motion_detected:
            self.last_motion_time = time.time()
            print("[IoTHub] PIR Motion DETECTED! High-priority inference activated.")
        else:
            print("[IoTHub] PIR Motion clear.")

    def is_inference_active(self):
        """
        Determines whether video processing should run at full 30 FPS or idle.
        Returns (is_active, current_mode)
        """
        if not self.pir_enabled:
            return True, "CONTINUOUS"
            
        if self.motion_detected:
            return True, "PIR_BURST"
            
        # Check timeout
        if time.time() - self.last_motion_time < self.motion_timeout_seconds:
            return True, "PIR_ACTIVE"
            
        return False, "POWER_SAVER"

    def record_esp32_heartbeat(self, ip_address):
        """Records node heartbeat from ESP32."""
        self.esp32_ip = ip_address
        self.esp32_last_heartbeat = time.time()

    def get_telemetry(self):
        """Returns comprehensive IoT telemetry for frontend dashboard."""
        now = time.time()
        is_active, mode = self.is_inference_active()
        esp32_online = bool(self.esp32_last_heartbeat > 0 and (now - self.esp32_last_heartbeat < 10.0))
        
        return {
            "pir_enabled": self.pir_enabled,
            "motion_detected": self.motion_detected,
            "last_motion_seconds_ago": round(now - self.last_motion_time, 1),
            "inference_mode": mode,
            "buzzer_state": self.buzzer_state,
            "esp32_online": esp32_online,
            "esp32_ip": self.esp32_ip
        }

# Global singleton instance
iot_hub = IoTHub()

if __name__ == "__main__":
    print("Testing IoTHub...")
    iot_hub.update_pir_motion(True)
    status = iot_hub.get_telemetry()
    print("IoT Telemetry:", status)
    assert status["motion_detected"] is True
    print("IoTHub tests passed!")
