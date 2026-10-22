# 👁️ RiskVision 2.0 — Multimodal AI-Powered Violence Detection & Response System

> Transforming passive surveillance into proactive, multimodal security that detects, confirms, and responds in real time.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-Deep%20Learning-00FFFF?style=flat-square&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Vision-27338e?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![ESP32-CAM](https://img.shields.io/badge/ESP32--CAM-IoT%20Wireless%20Node-E7352C?style=flat-square&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database%20%26%20Storage-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![Twilio](https://img.shields.io/badge/Twilio-SMS%20Alerts-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://www.twilio.com/)

---

## 📋 Overview

**RiskVision 2.0** is an enterprise-grade, proactive multimodal AI surveillance and deterrence ecosystem. Traditional surveillance is passive — it records incidents for later review rather than prevention. RiskVision 2.0 changes this by actively analyzing **both visual action signatures and acoustic distress cues**, fusing them to eliminate false alarms, and triggering on-site physical deterrence to disrupt violence before it escalates.

---

## 🌟 Key Innovations in RiskVision 2.0

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 RISKVISION 2.0 ARCHITECTURE                                 │
├──────────────────────────┬──────────────────────────┬───────────────────────────────────────┤
│ 1. Dual-Camera Network   │ 2. Multimodal AI Engine  │ 3. Escalated Response Router          │
│ • Camera 1: Laptop USB   │ • YOLOv11 Violence Model │ • Tier 1 (Low): Silent Dashboard Flag │
│ • Camera 2: ESP32-CAM    │ • YOLOv11 Weapon Model   │ • Tier 2 (Med): Twilio SMS + Clip     │
│   (Wireless Wi-Fi Node)  │ • MFCC Scream Detection  │ • Tier 3 (High): On-Site Siren + SMS  │
│ • Person Re-ID Tracking  │ • Audio-Visual Fusion    │ • PIR Motion Power-Saver Gating       │
└──────────────────────────┴──────────────────────────┴───────────────────────────────────────┘
```

| Feature | Description |
| :--- | :--- |
| 🔍 **Real-Time YOLOv11 Detection** | Custom fine-tuned weights (`best.pt`) detecting violent physical aggression with temporal persistence filtering to eliminate single-frame false positives. |
| 🎙️ **Acoustic Scream & Distress AI** | Native 48 kHz audio processing extracting **13 MFCC coefficients**, **Spectral Centroid (pitch shift)**, and **RMS Energy** to identify auditory cries for help. |
| ⚡ **Audio-Visual Fusion Engine** | Combines visual confidence ($60\%$) and acoustic scream score ($40\%$) into a unified threat metric: $S_{fusion} = 0.6 \cdot C_{video} + 0.4 \cdot C_{audio}$. |
| 🚨 **3-Tier Severity Router** | **Tier 1 (Low):** Visual only $\rightarrow$ Silent dashboard HUD flag.<br>**Tier 2 (Medium):** Video + Audio distress $\rightarrow$ Twilio SMS + Cloud clip.<br>**Tier 3 (High):** Weapon or high fusion score $\rightarrow$ Immediate SMS + On-site deterrence buzzer + video evidence. |
| 🔪 **Proactive Weapon Detection** | Detects weapons (knives, bats, scissors) before violence breaks out, immediately escalating to Tier 3 response. |
| 🔊 **Active Deterrence Actuator** | Automatically sounds an immediate audible warning alarm (laptop speakers + ESP32 GPIO 14 active buzzer) to disrupt incidents at the scene. |
| 👤 **Cross-Camera Person Re-ID** | Multi-zone Upper/Lower body HSV spatial color histograms and cosine similarity matching track `SUSPECT-01`, `SUSPECT-02` as they traverse between Camera 1 and Camera 2. |
| 🚶 **PIR Motion Sensor Gating** | HC-SR501 PIR sensor dynamically throttles processing: runs in lightweight **Power-Saver Mode** when rooms are empty and bursts to **Full 30 FPS** on movement. |
| 📹 **Multi-Camera Command Center** | Responsive dual-stream React dashboard featuring side-by-side feeds, real-time live mic distress gauge, PIR status badge, and buzzer controls. |
| ☁️ **Dual Cloud & Local Storage** | Automates rolling 10s buffer clip generation, pushes evidence to Supabase Storage with thumbnails, and maintains local disk fallbacks. |

---

## 🗂️ Project Structure

```text
RiskVision/
├── Backend/                        # Python API + Multimodal AI Subsystems
│   ├── eye-view.py                 # Main Flask server & dual-camera streaming routes
│   ├── audio_classifier.py         # Real-time microphone capture & MFCC scream detection
│   ├── fusion_engine.py            # Multimodal Audio-Visual Fusion & 3-Tier response router
│   ├── camera_manager.py           # Thread-safe dual camera manager (Webcam + ESP32-CAM)
│   ├── reid_tracker.py             # Cross-camera Person Re-ID tracking engine
│   ├── iot_hub.py                  # PIR motion gating & ESP32 telemetry gateway
│   ├── requirements.txt            # Python dependencies (Torch, Ultralytics, SoundDevice, etc.)
│   ├── best.pt                     # Fine-tuned YOLOv11 violence detection model
│   ├── yolo11n.pt                  # YOLOv11 model for weapon and person detection
│   └── users.json                  # Hashed user credentials & audit logs
│
├── EyeView-frontend/               # React 19 + Vite 6 Command Center
│   ├── src/
│   │   ├── pages/                  # Dashboard (Dual-Cam HUD), Alerts, History, Analytics
│   │   ├── components/             # Navbar, Sidebar, PrivateRoute, Form templates
│   │   └── context/                # JWT AuthContext
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite configuration
│
├── Hardware_Setup_Guide.md         # 🔌 Complete beginner-friendly hardware assembly & wiring guide
├── RiskVision_2.0_Audit_and_Roadmap.md # 📊 Comprehensive project audit & presentation mapping
└── README.md                       # Master Documentation
```

---

## 🔌 Hardware Setup (For Team & Evaluators)

RiskVision 2.0 uses an IoT sensor node composed of:
1. **ESP32-CAM (AI-Thinker) + OV2640 Camera:** Wireless Camera 2 node streaming over Wi-Fi.
2. **ESP32-CAM-MB Programmer Shield:** USB dock for flashing and power.
3. **HC-SR501 PIR Motion Sensor:** Motion-based AI inference gating on GPIO 13.
4. **5V Active Buzzer Module:** Active deterrence alarm trigger on GPIO 14.
5. **Breadboard & Jumper Wires:** Solderless 5V & GND power distribution.

👉 **See the complete step-by-step wiring guide & Arduino firmware in [Hardware_Setup_Guide.md](Hardware_Setup_Guide.md).**

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Lucky-939/RiskVision.git
cd RiskVision
```

### 2. Backend Setup (Python)
```bash
cd Backend

# Create & activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the RiskVision 2.0 backend
python eye-view.py
```
*API runs at **`http://localhost:5000`***

### 3. Frontend Setup (React / Vite)
```bash
# In a second terminal:
cd EyeView-frontend

# Install dependencies & run Vite dev server
npm install
npm run dev
```
*Dashboard available at **`http://localhost:5173`***

---

## 🔑 Environment Configuration

Create a `.env` file in `Backend/.env`:
```env
# Twilio SMS Emergency Configuration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
ADMIN_PHONE_NUMBER=+91XXXXXXXXXX

# Supabase Storage & Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# JWT Secret
JWT_SECRET_KEY=riskvision-super-secret-key-2026
```

---

## 📡 API Reference (Core Endpoints)

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/video_feed/cam1` | `GET` | MJPEG video stream for Camera 1 (Webcam) with HUD telemetry. |
| `/video_feed/cam2` | `GET` | MJPEG stream for Camera 2 (ESP32-CAM) with Person Re-ID tracking. |
| `/api/telemetry` | `GET` | Real-time JSON telemetry (Fusion score, audio volume, scream conf, PIR status). |
| `/api/sensor/pir` | `POST` | Webhook for ESP32 (or UI simulator) to report PIR motion. |
| `/api/actuator/buzzer` | `POST` | Fires the on-site deterrence siren (laptop speaker + ESP32 buzzer). |
| `/api/config/camera2` | `POST` | Dynamically updates Camera 2 IP stream URL. |
| `/api/suspects` | `GET` | Lists currently active suspects tracked across camera nodes. |
| `/alerts` | `GET` / `DELETE` | Returns recent alerts with color-coded severity tiers and suspect IDs. |

---

## 👥 Contributors

* **Aaryan Tawde** — VU4F2324133
* **Shivam Singh** — VU4F2324134
* **Jay Patil** — VU4F2324143
* **Lucky Bhoir** — VU4F2324150
* **Project Guide:** Dr. Kavita Wagh
