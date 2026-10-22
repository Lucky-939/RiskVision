"""
RiskVision 2.0 - Multimodal Fusion Engine & 3-Tier Severity Router
Fuses visual detection (YOLOv11) with acoustic scream/distress detection (MFCC + Centroid)
and routes responses across 3 distinct escalation tiers per Slide 4 specifications.
"""

import time
import threading
try:
    import winsound
except ImportError:
    winsound = None

class MultimodalFusionEngine:
    def __init__(self, weight_video=0.60, weight_audio=0.40):
        self.weight_video = weight_video
        self.weight_audio = weight_audio
        
        # State tracking
        self.last_fusion_score = 0.0
        self.current_tier = 0       # 0: Normal, 1: Low, 2: Medium, 3: High
        self.last_tier_time = 0.0
        self.buzzer_active = False
        
        # Cooldown management for real alerts (Tiers 2 and 3)
        self.cooldowns = {
            2: 12.0,  # Medium tier cooldown
            3: 15.0   # High tier cooldown
        }
        self.last_alert_timestamps = {2: 0.0, 3: 0.0}
        
        # Consecutive frame persistence counter for video
        self.consecutive_violence_count = 0
        self.required_persistence = 3 # Must persist for 3 frames to avoid false flicker
        
        # Hardware / ESP32 callback hook
        self.hardware_buzzer_callback = None

    def set_hardware_buzzer_callback(self, callback):
        self.hardware_buzzer_callback = callback

    def trigger_buzzer(self, duration_ms=1500, frequency=2800):
        """Sounds on-site deterrence buzzer (laptop speaker siren + ESP32 GPIO)."""
        def _buzzer_worker():
            self.buzzer_active = True
            print("[ACTUATOR] >>> ON-SITE DETERRENCE BUZZER ACTIVATED! <<<")
            if self.hardware_buzzer_callback:
                try:
                    self.hardware_buzzer_callback(True)
                except Exception as e:
                    print(f"[ACTUATOR] Hardware buzzer error: {e}")
            if winsound:
                try:
                    for _ in range(3):
                        winsound.Beep(frequency, 220)
                        time.sleep(0.08)
                except Exception:
                    pass
            else:
                time.sleep(duration_ms / 1000.0)
            if self.hardware_buzzer_callback:
                try:
                    self.hardware_buzzer_callback(False)
                except Exception:
                    pass
            self.buzzer_active = False

        threading.Thread(target=_buzzer_worker, daemon=True).start()

    def update_frame_persistence(self, raw_violence_detected):
        """Tracks consecutive frames to prevent single-frame flickering."""
        if raw_violence_detected:
            self.consecutive_violence_count += 1
        else:
            self.consecutive_violence_count = max(0, self.consecutive_violence_count - 1)
        return self.consecutive_violence_count >= self.required_persistence

    def evaluate(self, video_confidence, audio_confidence, weapon_detected=False, persistent_violence=False):
        """
        Multimodal Decision Logic according to Slide 4:
        - Tier 1 (Low): Video only (persistent), no audio confirmation -> Dashboard HUD flag, silent monitoring
        - Tier 2 (Medium): Video + Audio both confirm distress -> SMS + Cloud clip + Priority dashboard flag
        - Tier 3 (High): Weapon detected OR High-confidence fusion (>= 0.70) -> Immediate SMS + Siren + Clip
        """
        now = time.time()
        
        # Calculate fused confidence
        fused_score = (self.weight_video * video_confidence) + (self.weight_audio * audio_confidence)
        self.last_fusion_score = round(float(fused_score), 2)

        decision = {
            "tier": 0,
            "tier_label": "NORMAL",
            "fused_score": self.last_fusion_score,
            "video_conf": round(float(video_confidence), 2),
            "audio_conf": round(float(audio_confidence), 2),
            "weapon_detected": bool(weapon_detected),
            "actions": [],
            "trigger_alert": False
        }

        # ── TIER 3 — HIGH SEVERITY ──────────────────────────────────
        # Trigger: Weapon detected OR High-confidence fusion score (>= 0.70)
        if weapon_detected or (self.last_fusion_score >= 0.70 and persistent_violence):
            decision["tier"] = 3
            decision["tier_label"] = "HIGH"
            decision["actions"] = ["IMMEDIATE_SMS", "ON_SITE_BUZZER", "CRITICAL_DASHBOARD_FLAG", "SAVE_EVIDENCE_CLIP"]
            if now - self.last_alert_timestamps[3] >= self.cooldowns[3]:
                decision["trigger_alert"] = True
                self.last_alert_timestamps[3] = now
                self.trigger_buzzer()

        # ── TIER 2 — MEDIUM SEVERITY ────────────────────────────────
        # Trigger: Video + audio both confirm distress (Video >= 0.50, Audio >= 0.45)
        elif persistent_violence and video_confidence >= 0.50 and audio_confidence >= 0.45:
            decision["tier"] = 2
            decision["tier_label"] = "MEDIUM"
            decision["actions"] = ["CLOUD_SMS_ALERT", "PRIORITY_DASHBOARD_FLAG", "SAVE_EVIDENCE_CLIP"]
            if now - self.last_alert_timestamps[2] >= self.cooldowns[2]:
                decision["trigger_alert"] = True
                self.last_alert_timestamps[2] = now

        # ── TIER 1 — LOW SEVERITY ───────────────────────────────────
        # Trigger: Persistent video signal only, no audio confirmation (Video >= 0.52, Audio < 0.45)
        elif persistent_violence and video_confidence >= 0.52:
            decision["tier"] = 1
            decision["tier_label"] = "LOW"
            decision["actions"] = ["LOG_EVENT", "SILENT_DASHBOARD_FLAG", "SILENT_MONITORING"]
            # Per Slide 4: Tier 1 does NOT flood SMS or save clips every 5s; it only flags the live dashboard.
            decision["trigger_alert"] = False

        self.current_tier = decision["tier"]
        return decision

# Global singleton
fusion_engine = MultimodalFusionEngine()
