# 🛡️ RiskVision 2.0: Comprehensive Project Audit, Gap Analysis & Roadmap

---

## 📌 Executive Summary

This report establishes a definitive comparison between **what is currently built** in the EyeView repository and **what must be developed** to fulfill the **RiskVision 2.0** architecture presented in the project slides (*Multimodal AI-Powered Violence Detection & Response System* by Aaryan Tawde, Shivam Singh, Jay Patil, and Lucky Bhoir under Dr. Kavita Wagh).

---

## 1. 🔍 Detailed Audit of Completed Features (Current Codebase)

A comprehensive review of every file across the `Backend/` and `EyeView-frontend/` directories reveals the following completed capabilities:

| Component | File / Location | Status | What Has Actually Been Implemented |
| :--- | :--- | :---: | :--- |
| **Violence Detection (YOLOv11n)** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L50-L57), [`best.pt`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/best.pt) | ✅ **100% Ready** | Custom fine-tuned weights (`best.pt`) detecting 2 classes: `0: Non-violence`, `1: Violence`. Runs real-time inference on 640x640 letterboxed frames with confidence thresholding (`> 0.35`). |
| **Single-Camera Video Pipeline** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L59-L71) | ✅ **100% Ready** | Reads laptop camera via OpenCV `cv2.VideoCapture(0)` at 1280x720, calculates actual camera FPS, and draws bounding boxes/labels. |
| **MJPEG Live Streaming** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L311-L364), [`/video_feed`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L511-L514) | ✅ **100% Ready** | Streams JPEG frames using `multipart/x-mixed-replace` MIME type directly to the React frontend. |
| **Rolling Buffer Clip Recording** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L72-L76), [`save_clip()`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L248-L275) | ✅ **100% Ready** | A thread-safe `deque(maxlen=300)` captures a 10-second rolling buffer. On alert, a daemon thread encodes frames to MP4 using `imageio` (`libx264` codec, `yuv420p` pixel format) and extracts the 1st frame as a thumbnail. |
| **Dual Storage (Cloud + Local)** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L276-L309), [`alert_log.json`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/alert_log.json) | ✅ **100% Ready** | Uploads clips to Supabase Storage bucket `alert-media` and inserts rows into `violence_detections` and `history_clips`. Falls back gracefully to local directory [`Backend/static/history_clips/`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/static/history_clips/) and local JSON file if offline. |
| **SMS Alerting Pipeline** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L89-L96), [`send_alert()`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L186-L245) | ✅ **100% Ready** | Dispatches SMS messages via Twilio REST API to `ADMIN_PHONE_NUMBER` with timestamp, confidence, and location. Has a 10s cooldown (`ALERT_COOLDOWN`) to avoid spamming. |
| **Geolocation Tagging** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L175-L184) | ✅ **100% Ready** | Enriches alerts by calling `ip-api.com/json/` to fetch City, Region, and Country. |
| **JWT User Authentication** | [`Backend/eye-view.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/eye-view.py#L97-L164), [`EyeView-frontend/src/context/AuthContext.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/context/AuthContext.jsx) | ✅ **100% Ready** | SHA-256 hashed password storage in [`Backend/users.json`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/users.json), JWT generation and verification (`Flask-JWT-Extended`), register/login/profile endpoints. |
| **Live Monitoring Dashboard** | [`EyeView-frontend/src/pages/Dashboard.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/pages/Dashboard.jsx) | ✅ **100% Ready** | Single-camera stream display, play/pause toggles, fullscreen mode, real-time alert polling, and stat summary cards. |
| **Alert Management UI** | [`EyeView-frontend/src/pages/Alerts.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/pages/Alerts.jsx) | ✅ **100% Ready** | 5-second polling interval, alert cards with timestamp/location, video clip playback, and full alert deletion (`DELETE /alerts/<id>`). |
| **Evidence History UI** | [`EyeView-frontend/src/pages/History.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/pages/History.jsx) | ✅ **100% Ready** | History clip gallery with thumbnails, video player modal, and MP4 direct download capability. |
| **Analytics Dashboard** | [`EyeView-frontend/src/pages/Analytics.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/pages/Analytics.jsx) | ✅ **100% Ready** | Visualizes user logins and system metrics using `react-chartjs-2` and `chart.js`. |

---

## 2. 📊 PPT Analysis: What is New in RiskVision 2.0

Based on slides 1 through 7 of the presentation, the following **8 major innovations and components** must be built:

| Innovation / Feature | Slide | Specification in Presentation |
| :--- | :---: | :--- |
| **1. Multi-Camera Network (Dual-Feed)** | Slide 2, 3, 6 | **Camera 1:** Laptop Webcam (USB). **Camera 2:** Remote **ESP32-CAM** streaming live frames over Wi-Fi (RTSP/HTTP MJPEG). The dashboard and backend must simultaneously ingest and display both feeds. |
| **2. Audio Distress / Scream Detection** | Slide 2, 3, 5, 6 | Continuous microphone audio stream -> Audio preprocessing -> **MFCC (Mel-Frequency Cepstral Coefficients)** feature extraction -> **Audio Classifier** (detects screaming, cries for help, distress sounds). |
| **3. Audio-Visual Fusion Engine** | Slide 3, 4, 6 | Combines independent visual confidence ($C_{video}$) and audio scream confidence ($C_{audio}$) into a unified distress score ($S_{fusion}$) to dramatically reduce false alarms (e.g., dancing vs. real fights). |
| **4. 3-Tier Severity Response Router** | Slide 3, 4 | **Tier 1 (Low):** Video signal only (no audio). Action: Log event, silent dashboard flag.<br>**Tier 2 (Medium):** Video + Audio both confirm distress. Action: Cloud alert (SMS + push via Twilio/Firebase), priority dashboard flag.<br>**Tier 3 (High):** Weapon detected OR high-confidence fusion score. Action: Immediate cloud alert + **on-site buzzer** + critical UI flag + auto-save clip. |
| **5. Weapon Detection Pipeline** | Slide 4, 5 | Proactive threat identification detecting weapons (knives, guns, blunt weapons) before violence breaks out, triggering immediate Tier 3 response. |
| **6. Active Deterrence Actuator (Buzzer)** | Slide 3, 4, 5, 6 | Physical on-site buzzer/siren that sounds off locally at the scene when Tier 3 is triggered to interrupt violence in progress. |
| **7. Cross-Camera Person Re-ID Tracking** | Slide 3, 5, 6 | Assigns a consistent person ID when an incident occurs and tracks that suspect as they move across Camera 1 and Camera 2 views. |
| **8. PIR Motion Sensor & MQTT Broker** | Slide 3 | **PIR Motion Sensor:** Gated processing (activates heavy AI inference only when physical motion is detected to conserve CPU/power).<br>**MQTT Broker (Mosquitto):** Wi-Fi communication link connecting camera nodes, PIR sensor, Laptop server, and Dashboard. |

---

## 3. ⚖️ Gap Analysis (What's Ready vs. What Needs to be Built)

| Capability | Current State in Codebase | Target State in RiskVision 2.0 | Action Required |
| :--- | :--- | :--- | :--- |
| **Camera Inputs** | Single webcam (`cv2.VideoCapture(0)`) | Multi-camera: USB Webcam + remote ESP32-CAM stream | Add asynchronous multi-threaded stream receiver supporting RTSP/HTTP URL for Camera 2. Update frontend to show dual-camera grid. |
| **Audio Processing** | ❌ None (No audio libraries or mic input) | Continuous mic capture, MFCC extraction, scream model | Install `librosa` / `sounddevice` / `numpy`, build audio thread, load audio classifier. |
| **Decision Engine** | Single threshold (`confidence > 0.35`) | Dynamic 3-Tier Severity Logic & Fusion Engine | Implement `FusionEngine` class calculating fused score and routing actions according to Tiers 1, 2, and 3. |
| **Object Detection** | Detects only `Violence` / `Non-violence` | Detects `Violence` + `Weapons` (guns, knives) | Integrate weapon detection weights (or train/merge a dual-class model for violence + weapons). |
| **Hardware Actuation** | ❌ None (Cloud-only alerts) | Physical On-Site Buzzer via GPIO or MQTT/Serial | Connect buzzer to ESP32 / Arduino / GPIO or USB Relay; publish trigger command via MQTT. |
| **IoT Connectivity** | HTTP REST & Polling only | MQTT Broker (Mosquitto) over Wi-Fi | Setup Mosquitto broker; publish detections and receive PIR triggers over MQTT topics (`riskvision/camera2/pir`, `riskvision/alerts/buzzer`). |
| **Motion Gating** | 24/7 continuous frame inference | PIR sensor triggers inference | Subscribe to PIR topic: run lightweight/sleep mode until PIR reports motion. |
| **Suspect Tracking** | ❌ None | Cross-Camera Person Re-ID | Implement DeepSORT / ByteTrack or lightweight feature embedding (e.g. OSNet / MobileNet Re-ID) across camera 1 & 2. |
| **Frontend UI** | Single video feed layout | Dual camera grid + severity badges (Low/Med/High) + Audio indicator | Update Dashboard to 2-column camera view; add real-time audio distress meter and severity level tags. |

---

## 4. 🛒 Required Hardware Shopping List & Wiring Guide

To build the physical IoT and multi-camera prototype demonstrated in the presentation, purchase the following components. All are standard, inexpensive, and readily available:

### 4.1 Bill of Materials (BOM)

| # | Item Name | Purpose in RiskVision 2.0 | Approx. Cost (INR) |
| :-: | :--- | :--- | :-: |
| **1** | **ESP32-CAM (AI-Thinker) Module + OV2640 Camera** | Acts as **Camera 2 Node**; streams video over Wi-Fi to laptop. | ₹450 - ₹650 |
| **2** | **FTDI USB-to-TTL Serial Programmer (FT232RL) + Mini/Micro USB cable** | Needed to flash firmware/code onto the ESP32-CAM (since ESP32-CAM lacks a built-in USB port). *Alternatively, buy an ESP32-CAM MB Shield.* | ₹180 - ₹250 |
| **3** | **HC-SR501 or AM312 PIR Motion Sensor** | Motion detection sensor; wakes the system or gates AI processing. | ₹80 - ₹120 |
| **4** | **5V Active Buzzer Module (with transistor driver) or 5V Piezo Siren** | **Active Deterrence**; loud audible alarm triggered during Tier 3 events. | ₹40 - ₹80 |
| **5** | **USB Microphone / Laptop Integrated Mic / MAX9814 Electret Mic Module** | Captures ambient audio for scream/distress detection. *(Can use laptop's built-in mic directly for zero cost, or MAX9814 connected to ESP32).* | ₹0 - ₹250 |
| **6** | **Half-size Solderless Breadboard & 40x Jumper Wires (Male-to-Female, Male-to-Male)** | For plug-and-play wiring of sensor, buzzer, and microcontroller without soldering. | ₹120 - ₹180 |
| **7** | **5V 2A Power Adapter / Micro-USB Breakout** | Stable power supply for ESP32-CAM (Wi-Fi streaming draws up to 300mA peak). | ₹150 - ₹250 |
| **Total** | | | **~₹1,000 – ₹1,800** |

---

### 4.2 Step-by-Step Connection & Wiring Instructions

#### A. Flashing the ESP32-CAM using FTDI Programmer
*(If using the ESP32-CAM MB shield with micro-USB, simply plug in the USB cable. If using bare FTDI programmer, wire as follows):*

```
FTDI Programmer               ESP32-CAM
---------------------------------------
VCC (set jumper to 5V) ------> 5V
GND                    ------> GND
TX                     ------> U0R (U0RX)
RX                     ------> U0T (U0TX)
                              IO0 connected to GND (REQUIRED only while flashing!)
```
> **Flash Note:** Connect `IO0` to `GND` before powering on to put the board in Bootloader mode. Hit Flash in Arduino IDE, then unplug `IO0` from `GND` and press the Reset button to run the camera web server.

#### B. Connecting the PIR Motion Sensor (HC-SR501 / AM312)
```
PIR Sensor Pin                ESP32-CAM Pin (or Arduino Pin)
-----------------------------------------------------------
VCC (5V)               ------> 5V (Breadboard Power Rail)
GND                    ------> GND (Common Ground)
OUT (Digital Signal)   ------> GPIO 13 (or GPIO 12)
```
* **How it works:** When a person walks into the room, `OUT` goes `HIGH` (3.3V). The ESP32 detects this and publishes an MQTT message `riskvision/sensor/pir = MOTION_DETECTED` to the laptop server.

#### C. Connecting the Active Deterrence Buzzer Module
```
Buzzer Module Pin             ESP32-CAM Pin
-----------------------------------------------------------
VCC                    ------> 5V (or 3.3V)
GND                    ------> GND
I/O or SIG (Signal)    ------> GPIO 14 (or GPIO 15)
```
* **How it works:** When the laptop detects a Tier 3 event (Weapon or High-confidence fusion), it publishes `riskvision/actuator/buzzer = ON`. The ESP32 receives this via MQTT and sets GPIO 14 to `HIGH`, sounding the buzzer loudly.

#### D. Audio Input Setup (Scream Detection)
* **Recommended Architecture:** Use the **Laptop's USB / Built-in Microphone** via Python's `sounddevice` or `pyaudio` library. This guarantees high 44.1 kHz / 16 kHz sampling without overburdening the ESP32-CAM's limited ADC bandwidth.
* *(Alternative)*: An **I2S Microphone (INMP441)** can be connected to the ESP32 pins if a standalone audio IoT node is preferred.

---

## 5. 🗓️ Implementation Roadmap (Phased Development Plan)

The upgrade from EyeView v2.2 to RiskVision 2.0 is structured into 4 sequential phases:

```mermaid
flowchart LR
    P1[Phase 1: Multi-Camera & MQTT Backbone] --> P2[Phase 2: Audio Distress Detection]
    P2 --> P3[Phase 3: Fusion Engine & 3-Tier Routing]
    P3 --> P4[Phase 4: Weapons, Re-ID & Active Buzzer]
```

---

### 🔹 Phase 1: Multi-Camera Ingestion & MQTT IoT Backbone (Week 1)
* **Goal:** Stream from both the Laptop Webcam and ESP32-CAM simultaneously, integrated with Mosquitto MQTT.
* **Tasks:**
  1. Install and run **Eclipse Mosquitto MQTT Broker** on the laptop (`localhost:1883`).
  2. Flash ESP32-CAM with `CameraWebServer` sketch configured with local Wi-Fi credentials; note its IP (e.g., `http://192.168.1.150:81/stream`).
  3. Create a multi-threaded camera manager in Python ([`Backend/camera_manager.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/)) to capture frames from `Camera 1 (USB 0)` and `Camera 2 (ESP32-CAM stream)` concurrently without dropped frames.
  4. Expose dual video endpoints: `/video_feed/cam1` and `/video_feed/cam2`.
  5. Update [`EyeView-frontend/src/pages/Dashboard.jsx`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/EyeView-frontend/src/pages/Dashboard.jsx) with a responsive 2x1 grid displaying both live feeds.

---

### 🔹 Phase 2: Acoustic Scream & Distress Detection (Week 2)
* **Goal:** Capture background audio and classify distress sounds in real time.
* **Tasks:**
  1. Add audio libraries to backend: `pip install librosa sounddevice numpy scipy`.
  2. Implement an audio background thread [`Backend/audio_classifier.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/) recording 1-second rolling audio chunks from the microphone.
  3. Extract **MFCC (Mel-Frequency Cepstral Coefficients)** features (13 or 20 coefficients) + zero-crossing rate + spectral centroid.
  4. Train or load a lightweight pre-trained audio classifier (SVM, Random Forest, or 1D CNN trained on datasets like SINS or ESC-50 / Scream dataset) outputting `audio_confidence` (0.0 to 1.0).

---

### 🔹 Phase 3: Multimodal Fusion Engine & 3-Tier Response Logic (Week 3)
* **Goal:** Combine video and audio signals and route alerts by severity level.
* **Tasks:**
  1. Create [`Backend/fusion_engine.py`](file:///c:/Users/Lucky%20Bhoir/EyeView_v2/Backend/) with decision formula:
     $$S_{fusion} = w_v \cdot C_{video} + w_a \cdot C_{audio}$$
     *(e.g., $w_v = 0.6$, $w_a = 0.4$)*.
  2. Implement the **3-Tier Severity Router**:
     * **Tier 1 (Low):** $C_{video} > 0.40$ and $C_{audio} \le 0.30 \implies$ Log locally, push silent alert flag to dashboard.
     * **Tier 2 (Medium):** $C_{video} > 0.40$ and $C_{audio} > 0.40 \implies$ Priority dashboard banner + Twilio SMS + Supabase clip upload.
     * **Tier 3 (High):** $S_{fusion} > 0.75$ or Weapon Detected $\implies$ Immediate SMS + On-Site Buzzer pulse + High Severity tag.
  3. Update frontend alert badges to show color-coded tags: `Low (Blue)`, `Medium (Yellow)`, `High (Red)`.

---

### 🔹 Phase 4: Active Deterrence, Weapon Detection & Person Re-ID (Week 4)
* **Goal:** Activate physical deterrence, detect armed threats, and maintain suspect identity across cameras.
* **Tasks:**
  1. **Active Buzzer Actuation:** Backend publishes an MQTT message `riskvision/actuator/buzzer = ON` when Tier 3 triggers; ESP32-CAM triggers GPIO pin to sound buzzer for 3 seconds.
  2. **Weapon Detection Integration:** Add weapon detection capability (either by fine-tuning YOLO with knives/guns or running an ensemble detector on detected person crops).
  3. **Cross-Camera Person Re-ID:** Implement tracking (e.g. ByteTrack / Norfair) with appearance color-histogram or lightweight MobileNet embedding. When an incident occurs in Camera 1, assign `Suspect #ID-01`; if the same visual profile enters Camera 2, preserve `Suspect #ID-01`.
  4. Final system test with live demonstration run.

---

## 6. 📋 Summary Comparison Table

| Dimension | EyeView v2.2 (Current Repo) | RiskVision 2.0 (Target Presentation) | Progress |
| :--- | :--- | :--- | :---: |
| **Visual Detection** | Single-camera YOLOv11n (Violence) | Dual-camera YOLOv11n (Violence + Weapons) | 🟡 60% |
| **Audio Processing** | None | Real-time MFCC + Scream Classifier | 🔴 0% |
| **Decision Logic** | Single static confidence threshold | 3-Tier Severity Escalation & Fusion Engine | 🔴 0% |
| **Hardware / IoT** | Laptop Webcam only | ESP32-CAM + PIR Sensor + Active Buzzer | 🔴 0% |
| **Network Protocol**| HTTP REST & Client Polling | MQTT Broker (Mosquitto) over Wi-Fi | 🔴 0% |
| **Cloud & Storage** | Supabase Storage & Twilio SMS | Supabase/Firebase + Twilio + Local Caching | 🟢 100% |
| **Web Dashboard** | Single-cam, Alerts, History, Analytics | Dual-cam, Severity Tags, Audio Meter | 🟡 70% |
| **Tracking** | None | Cross-Camera Person Re-ID | 🔴 0% |
