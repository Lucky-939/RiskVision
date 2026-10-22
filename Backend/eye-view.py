from flask import Flask, Response, jsonify, send_from_directory, abort, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import cv2
from supabase import create_client, Client as SupabaseClient
from twilio.rest import Client as TwilioClient
from ultralytics import YOLO
import datetime
import time
import json
import requests
import os
import re
import subprocess
import imageio
from dotenv import load_dotenv
from threading import Thread, Lock
from collections import deque
import hashlib
import uuid
import numpy as np

# RiskVision 2.0 Subsystems
from audio_classifier import audio_engine
from fusion_engine import fusion_engine
from camera_manager import camera_manager
from reid_tracker import reid_tracker
from iot_hub import iot_hub

app = Flask(__name__, static_folder="static")
CORS(app)  # Allow all origins

# JWT Setup
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'riskvision-secure-secret-key-2026')
jwt = JWTManager(app)

# User storage
USERS_FILE = 'users.json'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

# --- Thread-safe Locks and Buffers ---
frame_lock = Lock()
last_alert_time = 0
ALERT_COOLDOWN = 10  # Seconds between alerts
CLIP_DURATION = 10   # Seconds
FPS = 30

# Frame buffer for Camera 1 clip recording (stores last CLIP_DURATION seconds)
MAX_BUFFER_SIZE = int(FPS * CLIP_DURATION)
frame_buffer = deque(maxlen=MAX_BUFFER_SIZE)

# --- Configuration ---
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = "alert-media"

# --- Models ---
try:
    violence_model = YOLO("best.pt")
    print("[AI Model] YOLO violence model (best.pt) loaded successfully.")
except Exception as e:
    print(f"[AI Model] Error loading violence model: {e}")
    violence_model = None

try:
    general_model = YOLO("yolo11n.pt")
    print("[AI Model] YOLO general/weapon model (yolo11n.pt) loaded successfully.")
except Exception as e:
    print(f"[AI Model] Error loading general model: {e}")
    general_model = None

# Known weapon class IDs in standard COCO (yolo11n.pt)
WEAPON_CLASSES = {
    43: "Knife",
    34: "Baseball Bat",
    76: "Scissors"
}

# --- Supabase Setup ---
supabase_client = None
try:
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("[Cloud] Supabase client initialized successfully.")
    else:
        print("[Cloud] Supabase credentials not found. Local fallback mode enabled.")
except Exception as e:
    print(f"[Cloud] Error initializing Supabase: {e}")
    supabase_client = None

# --- Twilio Setup ---
twilio_client = None
try:
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("[Cloud] Twilio client initialized.")
except Exception as e:
    print(f"[Cloud] Error initializing Twilio client: {e}")
    twilio_client = None

# --- Local Clip Directory ---
clip_save_dir = os.path.abspath("static/history_clips")
os.makedirs(clip_save_dir, exist_ok=True)

# --- User Management Functions ---
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, first_name, last_name):
    users = load_users()
    if email in users:
        return False, "User already exists"

    user_id = str(uuid.uuid4())
    users[email] = {
        'id': user_id,
        'email': email,
        'password': hash_password(password),
        'first_name': first_name,
        'last_name': last_name,
        'created_at': datetime.datetime.now().isoformat(),
        'analytics': {
            'login_count': 0,
            'last_login': None,
            'login_history': [],
            'total_alerts_viewed': 0,
            'total_clips_viewed': 0
        }
    }
    save_users(users)
    return True, user_id

def authenticate_user(email, password):
    users = load_users()
    user = users.get(email)
    if user and user['password'] == hash_password(password):
        current_time = datetime.datetime.now().isoformat()
        if 'analytics' not in user:
            user['analytics'] = {
                'login_count': 0,
                'last_login': None,
                'login_history': [],
                'total_alerts_viewed': 0,
                'total_clips_viewed': 0
            }
        user['analytics']['login_count'] += 1
        user['analytics']['last_login'] = current_time
        user['analytics']['login_history'].append({
            'timestamp': current_time,
            'ip': request.remote_addr
        })
        user['analytics']['login_history'] = user['analytics']['login_history'][-50:]
        save_users(users)
        return user
    return None

def get_location():
    """Fetches public IP location."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=4)
        response.raise_for_status()
        data = response.json()
        return f"{data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')}"
    except Exception:
        return "Local Station"

# --- Alert & Video Recording System ---
def send_alert(confidence, tier_info=None, suspect_id=None):
    """
    RiskVision 2.0 Escalated Alert Dispatcher.
    Routes notifications according to Tier 1, Tier 2, or Tier 3 logic.
    """
    global last_alert_time
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN:
        return

    last_alert_time = now
    timestamp = datetime.datetime.now()
    location = get_location()

    tier = tier_info.get("tier", 1) if tier_info else 1
    tier_label = tier_info.get("tier_label", "LOW") if tier_info else "LOW"
    fused_score = tier_info.get("fused_score", confidence) if tier_info else confidence
    audio_conf = tier_info.get("audio_conf", 0.0) if tier_info else 0.0
    weapon_detected = tier_info.get("weapon_detected", False) if tier_info else False

    clip_filename = f"clip_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
    if supabase_client:
        video_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{clip_filename}"
    else:
        video_url = f"http://localhost:5000/history_clips/{clip_filename}"

    alert_data = {
        "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "confidence": round(float(fused_score), 2),
        "video_confidence": round(float(confidence), 2),
        "audio_confidence": round(float(audio_conf), 2),
        "tier": tier,
        "tier_label": tier_label,
        "location": location,
        "video_url": video_url,
        "suspect_id": suspect_id or "N/A",
        "weapon_detected": weapon_detected,
        "alert_type": f"Tier {tier} ({tier_label}) - {'Weapon Detected' if weapon_detected else 'Violence Detected'}"
    }

    print(f"--- [ALERT DISPATCH] {alert_data['alert_type']} | Score: {alert_data['confidence']} ---")

    # 1. Fallback local logging
    with open("alert_log.json", "a") as log_file:
        log_file.write(json.dumps(alert_data) + "\n")

    # 2. Cloud Storage (Supabase)
    if supabase_client:
        try:
            supabase_client.table('violence_detections').insert({
                "time": alert_data["time"],
                "confidence": alert_data["confidence"],
                "location": alert_data["location"],
                "video_url": alert_data["video_url"]
            }).execute()
        except Exception as e:
            print(f"[Supabase] Error logging alert: {e}")

    # 3. Twilio SMS Notification (Tiers 2 & 3 only)
    if twilio_client and tier >= 2:
        try:
            if tier == 3:
                body = f"🚨 RISKVISION CRITICAL [TIER 3]: {'Weapon' if weapon_detected else 'Violence'} at {alert_data['time']} | Fused Score: {alert_data['confidence']:.2f} | On-Site Buzzer Triggered! Location: {alert_data['location']}"
            else:
                body = f"⚠️ RISKVISION ALERT [TIER 2]: Multimodal Violence Confirmed at {alert_data['time']} | Fused Score: {alert_data['confidence']:.2f} | Audio Conf: {alert_data['audio_confidence']:.2f} | Location: {alert_data['location']}"

            twilio_client.messages.create(
                body=body,
                from_=TWILIO_PHONE_NUMBER,
                to=ADMIN_PHONE_NUMBER
            )
            print("[Twilio] SMS alert sent successfully.")
        except Exception as e:
            print(f"[Twilio] SMS error: {e}")

    # 4. Save video clip asynchronously
    with frame_lock:
        frames_to_save = list(frame_buffer)
    Thread(target=save_clip, args=(clip_save_dir, clip_filename, frames_to_save)).start()

def save_clip(directory, filename, frames):
    """Encodes rolling frame buffer into MP4 and uploads to Supabase."""
    if not frames:
        return

    filepath = os.path.join(directory, filename)
    try:
        rgb_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
        imageio.mimwrite(filepath, rgb_frames, fps=FPS, format='FFMPEG', codec='libx264', pixelformat='yuv420p')
        
        # Thumbnail extraction
        thumbnail_filename = f"{os.path.splitext(filename)[0]}_thumb.jpg"
        thumbnail_path = os.path.join(directory, thumbnail_filename)
        cv2.imwrite(thumbnail_path, frames[0])
        print(f"[Clip] Saved: {filename} with thumbnail.")
    except Exception as e:
        print(f"[Clip] Error encoding video: {e}")
        return

    # Upload to Supabase Storage
    if supabase_client:
        try:
            with open(filepath, 'rb') as f:
                supabase_client.storage.from_(SUPABASE_BUCKET).upload(filename, f, {"content-type": "video/mp4"})
            video_public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(filename)

            thumb_public_url = None
            if os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as tf:
                    supabase_client.storage.from_(SUPABASE_BUCKET).upload(thumbnail_filename, tf, {"content-type": "image/jpeg"})
                thumb_public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(thumbnail_filename)

            supabase_client.table('history_clips').insert({
                "filename": filename,
                "timestamp": datetime.datetime.now().isoformat(),
                "storage_url": video_public_url,
                "thumb_url": thumb_public_url
            }).execute()
            print(f"[Supabase] Uploaded clip and metadata for: {filename}")
        except Exception as e:
            print(f"[Supabase] Storage upload error: {e}")

# --- Video Processing Pipelines ---
def generate_cam1_stream():
    """Camera 1 (Webcam) Processing Pipeline: YOLO Violence + Weapon + Audio Fusion."""
    while True:
        success, frame = camera_manager.get_cam1_frame()
        if not success or frame is None:
            time.sleep(0.03)
            continue

        # Add frame to rolling buffer
        with frame_lock:
            frame_buffer.append(frame.copy())

        # Audio distress state
        audio_telemetry = audio_engine.get_status()
        audio_conf = audio_telemetry["distress_confidence"]

        # Visual Detection
        max_violence_conf = 0.0
        violence_detected = False
        weapon_detected = False
        weapon_label = ""
        suspect_crop = None

        if violence_model:
            results = violence_model(frame, imgsz=640, verbose=False)
            for res in results:
                for box in res.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label_name = violence_model.names.get(cls_id, "")

                    # Check violence class - threshold calibrated to >= 0.52 to prevent false alarms on calm scenes
                    if (label_name.lower() == "violence" or cls_id == 0) and conf >= 0.52:
                        max_violence_conf = max(max_violence_conf, conf)
                        violence_detected = True
                        suspect_crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                        color = (0, 0, 255) # Red
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, f"Violence: {conf:.2f}", (x1, max(15, y1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
                    elif label_name.lower() == "non-violence" or cls_id == 1:
                        color = (0, 255, 0) # Green
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                        cv2.putText(frame, f"Normal: {conf:.2f}", (x1, max(15, y1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Temporal persistence: Requires at least 3 consecutive frames to confirm violence
        persistent_violence = fusion_engine.update_frame_persistence(violence_detected)

        # Proactive Weapon Check (runs if general_model available)
        if general_model and (violence_detected or audio_conf > 0.40):
            w_results = general_model(frame, imgsz=640, verbose=False)
            for w_res in w_results:
                for box in w_res.boxes:
                    w_cls = int(box.cls[0])
                    w_conf = float(box.conf[0])
                    if w_cls in WEAPON_CLASSES and w_conf > 0.35:
                        weapon_detected = True
                        weapon_label = WEAPON_CLASSES[w_cls]
                        wx1, wy1, wx2, wy2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (wx1, wy1), (wx2, wy2), (0, 140, 255), 3)
                        cv2.putText(frame, f"WEAPON: {weapon_label} ({w_conf:.2f})", (wx1, max(20, wy1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)

        # Evaluate through Multimodal Fusion Engine with persistence gating
        decision = fusion_engine.evaluate(
            video_confidence=max_violence_conf if persistent_violence else 0.0,
            audio_confidence=audio_conf,
            weapon_detected=weapon_detected,
            persistent_violence=persistent_violence
        )

        # Person Re-ID registration if Tier >= 2
        suspect_id = None
        if decision["tier"] >= 2 and suspect_crop is not None and suspect_crop.size > 0:
            suspect_id = reid_tracker.register_suspect(suspect_crop, camera_id="Camera-1")

        # Trigger alert if required by response router (Tier 2 and Tier 3)
        if decision["trigger_alert"]:
            send_alert(max_violence_conf, tier_info=decision, suspect_id=suspect_id)

        # --- Draw HUD Telemetry Header ---
        tier = decision["tier"]
        tier_colors = {
            0: (0, 200, 0),    # Green (Normal)
            1: (255, 180, 0),  # Blue/Cyan (Low)
            2: (0, 165, 255),  # Orange (Medium)
            3: (0, 0, 255)     # Red (High)
        }
        hud_color = tier_colors.get(tier, (0, 255, 0))
        tier_text = f"TIER {tier}: {decision['tier_label']}"
        hud_info = f"Fused: {decision['fused_score']:.2f} | Audio: {audio_conf:.2f} | Vid: {max_violence_conf:.2f}"
        if suspect_id:
            hud_info += f" | {suspect_id}"

        # Top overlay bar
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 36), (20, 20, 20), -1)
        cv2.putText(frame, tier_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hud_color, 2)
        cv2.putText(frame, hud_info, (220, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)

        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def generate_cam2_stream():
    """Camera 2 (ESP32-CAM Node) Processing Pipeline: Person Re-ID Tracking & Feed."""
    while True:
        success, frame = camera_manager.get_cam2_frame()
        if not success or frame is None:
            # Render standby canvas when ESP32 is not streaming
            canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(canvas, "Camera 2: ESP32-CAM Node Standby", (80, 220),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            cv2.putText(canvas, "Waiting for Wi-Fi stream on port 81...", (110, 260),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (130, 130, 130), 1)
            cv2.putText(canvas, f"ESP32 URL: {camera_manager.cam2_src}", (120, 300),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 180, 100), 1)
            _, buffer = cv2.imencode('.jpg', canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
            continue

        # Run Person Re-ID matching on Camera 2
        if general_model:
            results = general_model(frame, classes=[0], imgsz=480, verbose=False) # class 0 is person
            for res in results:
                for box in res.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                    matched_id, score = reid_tracker.match_suspect(crop)
                    
                    if matched_id:
                        # Draw Suspect Track Box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2) # Yellow
                        cv2.putText(frame, f"RE-ID: {matched_id} ({int(score*100)}%)", (x1, max(20, y1 - 8)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (180, 180, 180), 1)

        # Header bar
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 32), (30, 30, 30), -1)
        cv2.putText(frame, "Camera 2 (ESP32-CAM Node) - Re-ID Active", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- Streaming Routes ---
@app.route('/video_feed')
def video_feed():
    """Primary video feed (Camera 1 / Laptop Webcam) for existing frontend."""
    return Response(generate_cam1_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/cam1')
def video_feed_cam1():
    """Camera 1 stream endpoint."""
    return Response(generate_cam1_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/cam2')
def video_feed_cam2():
    """Camera 2 (ESP32-CAM Node) stream endpoint."""
    return Response(generate_cam2_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- RiskVision 2.0 Telemetry & Control Endpoints ---
def to_serializable(val):
    """Recursively converts numpy types (float32, int64, etc.) to standard Python types."""
    if isinstance(val, (np.floating, np.float32, np.float64)):
        return float(val)
    if isinstance(val, (np.integer, np.int32, np.int64)):
        return int(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    if isinstance(val, dict):
        return {k: to_serializable(v) for k, v in val.items()}
    if isinstance(val, list):
        return [to_serializable(v) for v in val]
    return val

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    """Comprehensive real-time telemetry for frontend dashboard."""
    try:
        audio_data = audio_engine.get_status()
        iot_data = iot_hub.get_telemetry()
        suspects = reid_tracker.get_active_suspects()

        tier_labels = ["NORMAL", "LOW", "MEDIUM", "HIGH"]
        tier = fusion_engine.current_tier if 0 <= fusion_engine.current_tier < len(tier_labels) else 0

        payload = {
            "status": "online",
            "timestamp": datetime.datetime.now().isoformat(),
            "fusion": {
                "fused_score": float(fusion_engine.last_fusion_score),
                "current_tier": int(tier),
                "tier_label": str(tier_labels[tier]),
                "buzzer_active": bool(fusion_engine.buzzer_active)
            },
            "audio": audio_data,
            "iot": iot_data,
            "suspects": suspects,
            "cameras": {
                "cam1_active": bool(getattr(camera_manager.cam1, 'is_opened', False)),
                "cam2_active": bool(getattr(camera_manager.cam2, 'is_opened', False)),
                "cam2_source": str(camera_manager.cam2_src)
            }
        }
        return jsonify(to_serializable(payload)), 200
    except Exception as e:
        print(f"[Telemetry Error] {e}")
        return jsonify({"status": "error", "message": str(e)}), 200

@app.route('/api/sensor/pir', methods=['GET', 'POST'])
def handle_pir():
    """Receives PIR motion updates from ESP32 or manual simulation."""
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        motion = data.get("motion", True)
        iot_hub.update_pir_motion(motion)
        return jsonify({"message": "PIR status updated", "motion_detected": motion}), 200
    return jsonify({"motion_detected": iot_hub.motion_detected, "mode": iot_hub.is_inference_active()[1]})

@app.route('/api/actuator/buzzer', methods=['POST'])
def trigger_buzzer_api():
    """Manual trigger to test on-site deterrence buzzer."""
    fusion_engine.trigger_buzzer()
    return jsonify({"message": "Buzzer activated for active deterrence", "state": True}), 200

@app.route('/api/config/camera2', methods=['POST'])
def configure_camera2():
    """Updates Camera 2 URL (e.g. when ESP32 IP is known)."""
    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL parameter required"}), 400
    camera_manager.set_cam2_source(url)
    return jsonify({"message": "Camera 2 source updated", "source": url}), 200

@app.route('/api/suspects', methods=['GET'])
def list_suspects():
    """Returns active suspects tracked across cameras."""
    return jsonify({"suspects": reid_tracker.get_active_suspects()})

# --- Standard App Routes (Preserved & Enhanced) ---
@app.route('/history_clips')
def list_clips():
    """Lists all saved video clips."""
    clips_array = []
    if supabase_client:
        try:
            res = supabase_client.table('history_clips').select('*').order('created_at', desc=True).execute()
            for row in res.data:
                clips_array.append({
                    "id": row["id"],
                    "filename": row["filename"],
                    "timestamp": row["timestamp"],
                    "url": row.get("storage_url"),
                    "thumbnail_url": row.get("thumb_url")
                })
            return jsonify(clips_array)
        except Exception as e:
            print(f"[Supabase] Error listing history clips: {e}")

    # Fallback to local files
    if not os.path.exists(clip_save_dir):
        return jsonify([])

    files = sorted(
        [f for f in os.listdir(clip_save_dir) if f.endswith('.mp4')],
        key=lambda f: os.path.getmtime(os.path.join(clip_save_dir, f)),
        reverse=True
    )
    for fn in files:
        fp = os.path.join(clip_save_dir, fn)
        ts = os.path.getmtime(fp)
        thumb_name = f"{os.path.splitext(fn)[0]}_thumb.jpg"
        thumb_path = os.path.join(clip_save_dir, thumb_name)
        thumb_url = f"/thumbnails/{thumb_name}" if os.path.exists(thumb_path) else None
        clips_array.append({
            "id": fn,
            "filename": fn,
            "timestamp": datetime.datetime.fromtimestamp(ts).isoformat(),
            "url": f"/history_clips/{fn}",
            "thumbnail_url": thumb_url
        })
    return jsonify(clips_array)

@app.route('/alerts')
def get_alerts():
    """Returns alerts with tier classifications."""
    alerts = []
    if supabase_client:
        try:
            res = supabase_client.table('violence_detections').select('*').order('created_at', desc=True).execute()
            for row in res.data:
                alerts.append({
                    "id": row.get("id"),
                    "timestamp": row["time"],
                    "location": row.get("location"),
                    "confidence": row["confidence"],
                    "tier": 2, # default if not recorded
                    "tier_label": "MEDIUM",
                    "notified": True,
                    "alert_type": "Violence Detected",
                    "video_url": row.get("video_url")
                })
            return jsonify({"alerts": alerts})
        except Exception as e:
            print(f"[Supabase] Error fetching alerts: {e}")

    # Local alert_log.json fallback
    try:
        with open("alert_log.json", "r") as f:
            for line in reversed(f.readlines()):
                if line.strip():
                    item = json.loads(line)
                    alerts.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": item.get("time"),
                        "location": item.get("location"),
                        "confidence": item.get("confidence"),
                        "tier": item.get("tier", 1),
                        "tier_label": item.get("tier_label", "LOW"),
                        "audio_confidence": item.get("audio_confidence", 0.0),
                        "suspect_id": item.get("suspect_id", "N/A"),
                        "notified": True,
                        "alert_type": item.get("alert_type", "Violence Detected"),
                        "video_url": item.get("video_url")
                    })
    except Exception:
        pass
    return jsonify({"alerts": alerts})

@app.route('/alerts/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    if not supabase_client:
        return jsonify({"message": "Alert removed locally"}), 200
    try:
        supabase_client.table('violence_detections').delete().eq('id', alert_id).execute()
        return jsonify({"message": "Alert deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history_clips/<path:filename>')
def stream_video(filename):
    return send_from_directory(clip_save_dir, filename, mimetype='video/mp4')

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    return send_from_directory(clip_save_dir, filename, mimetype='image/jpeg')

# --- Authentication Routes ---
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    fn = data.get('firstName', '')
    ln = data.get('lastName', '')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    ok, res = create_user(email, password, fn, ln)
    if ok:
        token = create_access_token(identity=email)
        return jsonify({'message': 'User registered', 'access_token': token, 'user': {'id': res, 'email': email}}), 201
    return jsonify({'error': res}), 409

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    user = authenticate_user(email, password)
    if user:
        token = create_access_token(identity=email)
        return jsonify({'message': 'Login successful', 'access_token': token, 'user': {'id': user['id'], 'email': user['email']}}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/auth/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    user_email = get_jwt_identity()
    users = load_users()
    user = users.get(user_email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if request.method == 'PUT':
        data = request.get_json() or {}
        for f in ['first_name', 'last_name']:
            if f in data:
                user[f] = data[f]
        save_users(users)
        return jsonify({'message': 'Profile updated', 'user': user}), 200
    return jsonify({'user': user}), 200

@app.route('/auth/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    user_email = get_jwt_identity()
    users = load_users()
    user = users.get(user_email, {})
    total_users = len(users)
    active_users = sum(1 for u in users.values() if u.get('analytics', {}).get('last_login'))
    return jsonify({
        'user_analytics': user.get('analytics', {}),
        'global_analytics': {
            'total_users': total_users,
            'active_users': active_users,
            'login_trends': {}
        }
    }), 200

if __name__ == "__main__":
    print("=======================================================")
    print("  🚀 RiskVision 2.0 Multimodal AI System Starting...  ")
    print("=======================================================")
    # 1. Start audio distress detection thread
    audio_engine.start()
    
    # 2. Start dual camera manager
    camera_manager.start()
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    finally:
        audio_engine.stop()
        camera_manager.stop()
