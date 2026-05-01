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
from dotenv import load_dotenv
from threading import Thread, Lock
from collections import deque
import hashlib
import uuid

app = Flask(__name__, static_folder="static")
CORS(app)  # Allow all origins

# JWT Setup
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
jwt = JWTManager(app)

# Simple user storage (in production, use a proper database)
USERS_FILE = 'users.json'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

# --- Thread-safe Locks and Buffers ---
frame_lock = Lock()  # Lock for accessing shared resources (frame buffer)
video_stream_lock = Lock() # Lock for reading from the video stream

# --- Configuration ---
load_dotenv()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = "alert-media"
ALERT_COOLDOWN = 10  # Seconds between alerts
CLIP_DURATION = 10 # Seconds

# --- YOLO Model ---
try:
    model = YOLO("best.pt")
    print("YOLO model loaded successfully.")
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

# --- Video Capture ---
video_stream = cv2.VideoCapture(0)
if not video_stream.isOpened():
    print("Error: Could not open webcam.")
else:
    video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # Get the actual FPS from the camera
    FPS = video_stream.get(cv2.CAP_PROP_FPS)
    if FPS == 0:
        FPS = 30 # Default if camera doesn't provide FPS
        video_stream.set(cv2.CAP_PROP_FPS, FPS)
    print(f"Webcam opened successfully. Resolution: 1280x720, FPS: {FPS}")

# --- Frame Buffer for Clip Saving ---
# Store the last CLIP_DURATION seconds of frames
MAX_BUFFER_SIZE = int(FPS * CLIP_DURATION) if 'FPS' in locals() else 300
frame_buffer = deque(maxlen=MAX_BUFFER_SIZE)

# --- Supabase Setup ---
supabase_client = None
try:
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("Supabase client initialized successfully.")
    else:
        print("Supabase credentials not found. Supabase features will be disabled.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase_client = None

# --- Twilio Setup ---
try:
    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print("Twilio client initialized.")
except Exception as e:
    print(f"Error initializing Twilio client: {e}")
    client = None

# --- User Management Functions ---
def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
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
        # Update login analytics
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

        # Keep only last 50 login records
        user['analytics']['login_history'] = user['analytics']['login_history'][-50:]

        save_users(users)
        return user
    return None

# --- Alert System ---
last_alert_time = 0

# --- Clip Saving Directory ---
# Save clips locally for ffmpeg processing, then upload to Supabase Storage
clip_save_dir = os.path.abspath("static/history_clips")
os.makedirs(clip_save_dir, exist_ok=True)
print(f"Clip save directory set to: {clip_save_dir}")


def get_location():
    """Fetches the public IP based location."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"{data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')}"
    except requests.exceptions.RequestException as e:
        print(f"Could not get location: {e}")
        return "Unknown Location"

def send_alert(confidence):
    """Handles the alerting logic: logging, Supabase push, and Twilio SMS."""
    global last_alert_time
    current_time = time.time()
    if current_time - last_alert_time < ALERT_COOLDOWN:
        print("Alert in cooldown period. Skipping.")
        return

    print("--- ALERT TRIGGERED ---")
    last_alert_time = current_time
    timestamp = datetime.datetime.now()
    location = get_location()

    # Generate clip filename
    clip_filename = f"clip_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"

    # Pre-compute the Supabase public URL for this clip
    if supabase_client:
        video_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{clip_filename}"
    else:
        video_url = f"http://localhost:5000/history_clips/{clip_filename}"

    alert_data = {
        "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "confidence": round(confidence, 2),
        "location": location,
        "video_url": video_url
    }

    # Log alert locally as fallback
    with open("alert_log.json", "a") as log_file:
        log_file.write(json.dumps(alert_data) + "\n")

    # Push to Supabase
    if supabase_client:
        try:
            supabase_client.table('violence_detections').insert(alert_data).execute()
            print("Alert pushed to Supabase.")
        except Exception as e:
            print(f"Error pushing alert to Supabase: {e}")

    # Send SMS via Twilio
    if client:
        try:
            message_body = f"Violence detected at {alert_data['time']} | Confidence: {alert_data['confidence']:.2f} | Location: {alert_data['location']}"
            client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=ADMIN_PHONE_NUMBER
            )
            print("Twilio alert SMS sent.")
        except Exception as e:
            print(f"Error sending Twilio SMS: {e}")

    # Save the clip from the buffer in a new thread
    with frame_lock:
        frames_to_save = list(frame_buffer)
    
    Thread(target=save_clip, args=(clip_save_dir, clip_filename, frames_to_save)).start()

import imageio

def save_clip(directory, filename, frames):
    """Saves a list of frames to a video file using imageio, then uploads to Supabase Storage."""
    if not frames:
        print("Clip save failed: No frames in the buffer.")
        return

    filepath = os.path.join(directory, filename)
    print(f"Saving clip to: {filepath} ({len(frames)} frames)")

    try:
        # Convert BGR (OpenCV) to RGB for imageio
        rgb_frames = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
        
        # Write to mp4 using imageio (uses bundled ffmpeg)
        # fps=FPS is important so it's not sped up or slowed down
        imageio.mimwrite(filepath, rgb_frames, fps=FPS, format='FFMPEG', codec='libx264', pixelformat='yuv420p')
        print(f"Clip successfully saved: {filename}")

        # Generate thumbnail from the first frame
        thumbnail_filename = f"{os.path.splitext(filename)[0]}_thumb.jpg"
        thumbnail_path = os.path.join(directory, thumbnail_filename)
        cv2.imwrite(thumbnail_path, frames[0])
        print(f"Thumbnail generated: {thumbnail_filename}")

    except Exception as e:
        print(f"Failed to create video with imageio: {e}")
        return

    # Upload to Supabase Storage and save metadata
    if supabase_client:
        try:
            # Upload video file
            with open(filepath, 'rb') as f:
                supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                    filename, f, {"content-type": "video/mp4"}
                )
            video_public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
            print(f"Video uploaded to Supabase Storage: {filename}")

            # Upload thumbnail if it exists
            thumb_public_url = None
            if os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as tf:
                    supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                        thumbnail_filename, tf, {"content-type": "image/jpeg"}
                    )
                thumb_public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(thumbnail_filename)
                print(f"Thumbnail uploaded to Supabase Storage: {thumbnail_filename}")

            # Insert clip metadata into Supabase table
            clip_metadata = {
                "filename": filename,
                "timestamp": datetime.datetime.now().isoformat(),
                "storage_url": video_public_url,
                "thumb_url": thumb_public_url
            }
            supabase_client.table('history_clips').insert(clip_metadata).execute()
            print(f"Clip metadata for {filename} saved to Supabase.")

        except Exception as e:
            print(f"Error uploading clip to Supabase Storage: {e}")


def detect_and_stream():
    """
    Main loop to read frames, run detection, update buffer, and yield frames for streaming.
    """
    if not model:
        print("YOLO model not loaded. Cannot start detection.")
        return

    while True:
        with video_stream_lock:
            if not video_stream.isOpened():
                print("Webcam is not available. Retrying...")
                time.sleep(2)
                continue
            success, frame = video_stream.read()

        if not success:
            continue

        # Add a copy of the frame to our buffer for potential clip saving
        with frame_lock:
            frame_buffer.append(frame.copy())
        
        # --- Run YOLO Detection ---
        # Pass the original frame directly. Ultralytics YOLO handles letterboxing (aspect-ratio preserving resize)
        # and scales the bounding boxes back to the original image dimensions automatically.
        results = model(frame, imgsz=640, verbose=False)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                if class_id == 1:
                    label = "Violence"
                    color = (0, 0, 255) # Red
                    # Lowered threshold to 0.35 for maximum responsiveness during presentation
                    if confidence > 0.35:
                        send_alert(confidence)
                else:
                    label = "Non-violence"
                    color = (0, 255, 0) # Green

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label}: {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- Authentication Routes ---

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    success, result = create_user(email, password, first_name, last_name)
    if success:
        access_token = create_access_token(identity=email)
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': result,
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            }
        }), 201
    else:
        return jsonify({'error': result}), 409

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = authenticate_user(email, password)
    if user:
        access_token = create_access_token(identity=email)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    users = load_users()
    user = users.get(current_user)
    if user:
        return jsonify({
            'user': {
                'id': user['id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'created_at': user['created_at']
            }
        }), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    data = request.get_json()

    users = load_users()
    if current_user not in users:
        return jsonify({'error': 'User not found'}), 404

    # Update allowed fields
    allowed_fields = ['first_name', 'last_name']
    for field in allowed_fields:
        if field in data:
            users[current_user][field] = data[field]

    save_users(users)

    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'id': users[current_user]['id'],
            'email': users[current_user]['email'],
            'first_name': users[current_user]['first_name'],
            'last_name': users[current_user]['last_name'],
            'created_at': users[current_user]['created_at']
        }
    }), 200

@app.route('/auth/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    current_user = get_jwt_identity()
    users = load_users()
    user = users.get(current_user)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Get all users for admin stats (simplified - in production, check admin role)
    all_users = load_users()

    # Calculate analytics
    total_users = len(all_users)
    active_users = sum(1 for u in all_users.values() if u.get('analytics', {}).get('last_login'))

    # Login trends (last 7 days)
    login_trends = {}
    for u in all_users.values():
        history = u.get('analytics', {}).get('login_history', [])
        for login in history[-30:]:  # Last 30 logins
            date = login['timestamp'][:10]  # YYYY-MM-DD
            login_trends[date] = login_trends.get(date, 0) + 1

    # User-specific analytics
    user_analytics = user.get('analytics', {
        'login_count': 0,
        'last_login': None,
        'login_history': [],
        'total_alerts_viewed': 0,
        'total_clips_viewed': 0
    })

    return jsonify({
        'user_analytics': user_analytics,
        'global_analytics': {
            'total_users': total_users,
            'active_users': active_users,
            'login_trends': login_trends
        }
    }), 200

# --- Flask Routes ---

@app.route('/video_feed')
def video_feed():
    """Route for the video stream."""
    return Response(detect_and_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/history_clips')
def list_clips():
    """
    Lists all saved video clips from Supabase, with local filesystem fallback.
    """
    clips_array = []

    if supabase_client:
        try:
            response = supabase_client.table('history_clips').select('*').order('created_at', desc=True).execute()
            for row in response.data:
                clips_array.append({
                    "id": row["id"],
                    "filename": row["filename"],
                    "timestamp": row["timestamp"],
                    "url": row.get("storage_url"),
                    "thumbnail_url": row.get("thumb_url")
                })
            return jsonify(clips_array)
        except Exception as e:
            print(f"Error fetching history clips from Supabase: {e}")

    # Fallback: read from local filesystem
    if not os.path.exists(clip_save_dir):
        return jsonify([])

    files = sorted(
        [f for f in os.listdir(clip_save_dir) if f.endswith('.mp4')],
        key=lambda f: os.path.getmtime(os.path.join(clip_save_dir, f)),
        reverse=True
    )

    for filename in files:
        filepath = os.path.join(clip_save_dir, filename)
        timestamp = os.path.getmtime(filepath)

        thumbnail_filename = f"{os.path.splitext(filename)[0]}_thumb.jpg"
        thumbnail_path = os.path.join(clip_save_dir, thumbnail_filename)
        thumbnail_url = f"/thumbnails/{thumbnail_filename}" if os.path.exists(thumbnail_path) else None

        clips_array.append({
            "id": filename,
            "filename": filename,
            "timestamp": datetime.datetime.fromtimestamp(timestamp).isoformat(),
            "url": f"/history_clips/{filename}",
            "thumbnail_url": thumbnail_url
        })
    return jsonify(clips_array)


@app.route('/alerts')
def get_alerts():
    """Gets alerts from Supabase, with fallback to local log file."""
    alerts = []

    if supabase_client:
        try:
            response = supabase_client.table('violence_detections').select('*').order('created_at', desc=True).execute()
            for row in response.data:
                alerts.append({
                    "id": row.get("id"),
                    "timestamp": row["time"],
                    "location": row.get("location"),
                    "confidence": row["confidence"],
                    "notified": True,
                    "alert_type": "Violence Detected",
                    "video_url": row.get("video_url")
                })
            return jsonify({"alerts": alerts})
        except Exception as e:
            print(f"Error fetching alerts from Supabase: {e}")

    # Fallback: read from local log file
    try:
        with open("alert_log.json", "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if line.strip():
                    alert = json.loads(line)
                    alerts.append({
                        "id": str(uuid.uuid4()), # Fake ID for local fallback
                        "timestamp": alert["time"],
                        "location": alert["location"],
                        "confidence": alert["confidence"],
                        "notified": True,
                        "alert_type": "Violence Detected",
                        "video_url": alert.get("video_url")
                    })
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return jsonify({"alerts": alerts})

@app.route('/alerts/<alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    if not supabase_client:
        return jsonify({"error": "Supabase not configured"}), 500
        
    try:
        # First get the alert to find its video_url
        alert_res = supabase_client.table('violence_detections').select('video_url').eq('id', alert_id).execute()
        
        # Delete the alert from violence_detections
        supabase_client.table('violence_detections').delete().eq('id', alert_id).execute()
        
        # Also clean up history_clips if video_url exists
        if alert_res.data and alert_res.data[0].get('video_url'):
            video_url = alert_res.data[0]['video_url']
            
            # Find and delete from history_clips
            clip_res = supabase_client.table('history_clips').select('id, filename, thumb_url').eq('storage_url', video_url).execute()
            
            if clip_res.data:
                clip_data = clip_res.data[0]
                clip_id = clip_data['id']
                filename = clip_data['filename']
                thumb_url = clip_data.get('thumb_url')
                
                # Delete from history_clips table
                supabase_client.table('history_clips').delete().eq('id', clip_id).execute()
                
                # Delete from storage
                files_to_remove = [filename]
                if thumb_url:
                    thumb_filename = thumb_url.split('/')[-1]
                    files_to_remove.append(thumb_filename)
                
                supabase_client.storage.from_(SUPABASE_BUCKET).remove(files_to_remove)

        return jsonify({"message": "Alert deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting alert: {e}")
        return jsonify({"error": str(e)}), 500

# Local file serving routes (used as fallback when Supabase is unavailable)
@app.route('/history_clips/<path:filename>')
def stream_video(filename):
    """Serves a specific video clip file from local storage."""
    return send_from_directory(clip_save_dir, filename, mimetype='video/mp4')

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serves a specific thumbnail image from local storage."""
    return send_from_directory(clip_save_dir, filename, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
