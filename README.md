# 👁️ RiskVision — Real-Time AI Violence Detection System

> Protecting communities with intelligent, automated threat detection and instant emergency alerts.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![YOLOv11](https://img.shields.io/badge/YOLOv11-Deep%20Learning-00FFFF?style=flat-square&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Vision-27338e?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-Storage%20%26%20Auth-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Twilio](https://img.shields.io/badge/Twilio-SMS%20%26%20Calls-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS%204-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

---

## 📋 Overview

**RiskVision** (formerly EyeView) is a comprehensive, full-stack AI surveillance platform that performs real-time violence detection from live camera feeds using **YOLOv11n** deep learning models. 

When a threat or violent behavior is detected, the system instantly auto-records the incident, stores the video evidence securely in **Firebase Cloud Storage**, and dispatches automated SMS and voice call alerts to authorities via **Twilio** — all monitored through a modern, responsive **React dashboard**.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 **Real-Time AI Detection** | YOLOv11n-powered violence detection with low-latency video processing. |
| 📹 **Auto-Evidence Capture** | Incident clips are recorded and uploaded to Firebase Cloud Storage instantly. |
| 📲 **Instant SOS Alerts** | Twilio dispatches SMS and Voice Call emergency notifications to authorities. |
| 📊 **Live Monitoring Dashboard** | Real-time React dashboard showing live feed, alerts, and incident history. |
| 🎞️ **Incident History & Playback** | Full log of past detections with timestamps, clip playbacks, and auto-thumbnails. |
| 🔐 **Secure Authentication** | Firebase JWT-based access control for dashboard operators. |

---

## 🧠 Tech Stack

**AI & Computer Vision (Backend)**
* **Python 3.8+** — Core backend language
* **Flask** — API server & video streaming
* **YOLOv11n (Ultralytics)** — State-of-the-art real-time object & violence detection
* **OpenCV** — Video frame capture, processing, and clip rendering

**Frontend Dashboard**
* **React 19 & Vite 6** — Lightning-fast frontend framework
* **Tailwind CSS 4** — Utility-first responsive UI styling
* **Framer Motion** — Smooth animations and transitions
* **Axios** — HTTP client for backend API communication

**Cloud & Integrations**
* **Firebase** — Cloud Storage (evidence clips) & Authentication
* **Twilio** — Automated SMS and Programmable Voice APIs

---

## 🛠️ How It Works (Workflow)

1. **Frame Capture:** OpenCV reads continuous frames from the configured camera (webcam/IP).
2. **AI Inference:** The YOLOv11n model analyzes frames for violent behavior patterns.
3. **Threshold Filtering:** Detections above a confidence threshold trigger the alert pipeline.
4. **Evidence Recording:** OpenCV buffers the frames around the incident and saves it as an `.mp4` clip.
5. **Cloud Sync:** The clip (with auto-generated thumbnails) is pushed to Firebase Storage.
6. **Alert Dispatch:** Twilio fires an SMS and Voice Call to emergency contacts.
7. **Dashboard Update:** The React frontend updates in real-time, showing the new alert and clip link.

---

## 🗂️ Project Structure

```text
RiskVision/
├── Backend/                        # Python API + YOLO AI Engine
│   ├── eye-view.py                 # Main backend application
│   ├── requirements.txt            # Python dependencies
│   ├── best.pt                     # Trained YOLOv11n model weights
│   ├── alert_log.json              # Local alert history log
│   └── .env                        # Backend environment variables
│
├── EyeView-frontend/               # React + Vite Monitoring Dashboard
│   ├── src/
│   │   ├── components/             # Reusable UI (Alerts, Video Feed, Navbar)
│   │   ├── pages/                  # Dashboard, History, Alerts, Login
│   │   └── utils/                  # Firebase SDK config & API helpers
│   ├── package.json                # Frontend dependencies
│   └── .env                        # Frontend environment variables
│
└── README.md                       # Documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Node.js 18+** & npm
- A **Firebase Account** (Storage & Auth enabled)
- A **Twilio Account**

### 1. Clone the Repository
```bash
git clone https://github.com/Lucky-939/RiskVision.git
cd RiskVision
```

### 2. Backend Setup (Python)
```bash
cd Backend
python -m venv venv

# Activate Virtual Environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
> **Note:** Place your Firebase Admin SDK JSON file inside the `Backend/` directory and configure your `.env`.

### 3. Frontend Setup (React/Node)
```bash
cd ../EyeView-frontend
npm install
```

---

## 🔑 Environment Variables

You need to create two `.env` files.

**1. `Backend/.env`**
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
ADMIN_PHONE_NUMBER=+91XXXXXXXXXX

FIREBASE_CREDENTIALS_PATH=./your-firebase-adminsdk.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

DETECTION_CONFIDENCE=0.65
ALERT_COOLDOWN_SECONDS=30
CAMERA_SOURCE=0  # 0 for webcam, or use RTSP URL
```

**2. `EyeView-frontend/.env`**
```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

VITE_API_BASE_URL=http://localhost:5000
```

---

## 🚀 Running the Application

**Start the Backend (Terminal 1):**
```bash
cd Backend
.\venv\Scripts\activate
python eye-view.py
```
*API runs on `http://localhost:5000`*

**Start the Frontend (Terminal 2):**
```bash
cd EyeView-frontend
npm run dev
```
*Dashboard runs on `http://localhost:5173`*

---

## 🤝 Contributing

Contributions are always welcome! Whether it's improving detection accuracy, enhancing the UI, or optimizing performance.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

---

*Made with ❤️ for a safer world — [Lucky-939](https://github.com/Lucky-939)*
