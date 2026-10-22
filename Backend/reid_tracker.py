"""
RiskVision 2.0 - Cross-Camera Person Re-Identification (Person Re-ID)
Tracks suspects across Camera 1 and Camera 2 by extracting appearance color-spatial signatures
(HSV color histograms + aspect ratios) and matching them using Cosine Distance.
"""

import cv2
import numpy as np
import time

class SuspectReIDTracker:
    def __init__(self, similarity_threshold=0.68, gallery_ttl_seconds=120):
        self.similarity_threshold = similarity_threshold
        self.gallery_ttl_seconds = gallery_ttl_seconds
        
        # Suspect gallery: { suspect_id: { "signature": np.array, "first_seen": timestamp, "last_camera": str } }
        self.gallery = {}
        self.next_id = 1

    def extract_signature(self, crop):
        """
        Extracts multi-zone HSV color histogram signature from cropped person image.
        Splits person into Upper Body (torso) and Lower Body (legs) for robust clothing matching.
        """
        if crop is None or crop.size == 0 or crop.shape[0] < 20 or crop.shape[1] < 20:
            return None
            
        h, w, _ = crop.shape
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        
        # Upper body (torso: 0% - 60% height)
        upper = hsv[:int(h * 0.60), :]
        # Lower body (legs: 60% - 100% height)
        lower = hsv[int(h * 0.60):, :]
        
        # 8 Hue bins, 8 Saturation bins = 64 bins
        hist_upper = cv2.calcHist([upper], [0, 1], None, [8, 8], [0, 180, 0, 256])
        cv2.normalize(hist_upper, hist_upper, 0, 1, cv2.NORM_MINMAX)
        
        hist_lower = cv2.calcHist([lower], [0, 1], None, [8, 8], [0, 180, 0, 256])
        cv2.normalize(hist_lower, hist_lower, 0, 1, cv2.NORM_MINMAX)
        
        # Combined feature vector (128 dimensions)
        signature = np.concatenate([hist_upper.flatten(), hist_lower.flatten()])
        norm = np.linalg.norm(signature)
        if norm > 1e-6:
            signature = signature / norm
        return signature

    def register_suspect(self, crop, camera_id="Camera-1"):
        """Registers a new suspect involved in a Tier 2 / Tier 3 incident."""
        sig = self.extract_signature(crop)
        if sig is None:
            return None
            
        # Check if already in gallery
        matched_id, score = self.match_suspect(crop)
        if matched_id:
            # Update last seen camera
            self.gallery[matched_id]["last_seen"] = time.time()
            self.gallery[matched_id]["last_camera"] = camera_id
            return matched_id

        suspect_id = f"SUSPECT-{self.next_id:02d}"
        self.next_id += 1
        
        self.gallery[suspect_id] = {
            "signature": sig,
            "created_at": time.time(),
            "last_seen": time.time(),
            "last_camera": camera_id
        }
        print(f"[Person Re-ID] Registered new suspect: {suspect_id} from {camera_id}")
        return suspect_id

    def match_suspect(self, crop):
        """
        Compares person crop against active suspect gallery.
        Returns (matched_id, similarity_score) or (None, 0.0)
        """
        sig = self.extract_signature(crop)
        if sig is None or not self.gallery:
            return None, 0.0

        self._cleanup_expired()

        best_match = None
        best_score = 0.0

        for s_id, record in self.gallery.items():
            # Cosine similarity between normalized vectors = dot product
            score = float(np.dot(sig, record["signature"]))
            if score > best_score:
                best_score = score
                best_match = s_id

        if best_score >= self.similarity_threshold:
            return best_match, round(best_score, 2)
        return None, round(best_score, 2)

    def _cleanup_expired(self):
        """Prunes suspects after gallery TTL."""
        now = time.time()
        expired = [s_id for s_id, rec in self.gallery.items() if now - rec["last_seen"] > self.gallery_ttl_seconds]
        for s_id in expired:
            del self.gallery[s_id]

    def get_active_suspects(self):
        """Returns list of suspects currently tracked."""
        self._cleanup_expired()
        return [
            {
                "id": s_id,
                "first_seen": rec["created_at"],
                "last_seen": rec["last_seen"],
                "last_camera": rec["last_camera"]
            }
            for s_id, rec in self.gallery.items()
        ]

# Global singleton instance
reid_tracker = SuspectReIDTracker()

if __name__ == "__main__":
    print("Testing SuspectReIDTracker...")
    # Create fake person crop
    fake_crop1 = np.full((120, 60, 3), (120, 50, 200), dtype=np.uint8)
    s_id = reid_tracker.register_suspect(fake_crop1, camera_id="Camera-1")
    print(f"Registered suspect: {s_id}")
    
    # Test matching on similar crop (e.g. on Camera 2)
    fake_crop2 = np.full((120, 60, 3), (122, 52, 198), dtype=np.uint8)
    matched, conf = reid_tracker.match_suspect(fake_crop2)
    print(f"Camera 2 Match result: {matched} with confidence {conf}")
    assert matched == s_id
    print("Person Re-ID test passed!")
