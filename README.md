# 👁️ RiskVision — Real-Time AI Violence Detection System

> Protecting communities with intelligent, automated threat detection and instant emergency alerts.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![YOLO](https://img.shields.io/badge/YOLO-Deep%20Learning-00FFFF?style=flat-square&logo=yolo&logoColor=black)](https://ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Vision-27338e?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)](https://vitejs.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-Storage%20%26%20Auth-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Twilio](https://img.shields.io/badge/Twilio-SMS%20%26%20Calls-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS%204-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue?style=flat-square)](LICENSE)

---

**RiskVision** (internally named EyeView) is a full-stack AI-powered public safety platform that performs real-time violence detection from live camera feeds using **YOLO deep learning** models. When a threat is detected, it automatically records video evidence, stores it in **Firebase Cloud Storage**, and dispatches instant SMS and voice call alerts to authorities via **Twilio** — all visualised on a live **React** dashboard.

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [🛠️ How It Works](#️-how-it-works)
- [🗂️ Project Structure](#️-project-structure)
- [🧠 Tech Stack](#-tech-stack)
- [🤖 YOLO Detection Engine](#-yolo-detection-engine)
- [🔥 Firebase Integration](#-firebase-integration)
- [📲 Twilio Alert System](#-twilio-alert-system)
- [⚙️ Installation](#️-installation)
- [🔑 Environment Configuration](#-environment-configuration)
- [🚀 Running the Application](#-running-the-application)
- [🐛 Troubleshooting](#-troubleshooting)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description | Status |
|---|---|---|
| 🔍 **Real-Time Detection** | YOLO-powered violence detection with low-latency video processing | ✅ Active |
| 📹 **Automatic Evidence Recording** | Incident clips recorded and uploaded to Firebase Cloud Storage instantly | ✅ Active |
| 📲 **Instant SMS & Voice Alerts** | Twilio sends emergency notifications to configured authority numbers | ✅ Active |
| 📊 **Live Monitoring Dashboard** | Real-time React dashboard showing live feed, alerts, and incident history | ✅ Active |
| 📱 **Mobile Camera Support** | Compatible with mobile device camera streams | ✅ Active |
| 🔐 **Firebase Authentication** | Secure access control for the monitoring dashboard | ✅ Active |
| 🏙️ **Smart City Ready** | Designed for deployment in public CCTV and surveillance environments | ✅ Active |
| 🎞️ **Incident History** | Full log of past detections with timestamps, clips, and alert records | ✅ Active |

---

## 🛠️ How It Works

```
📷 Live Camera Feed
        │
        ▼
  OpenCV captures frames continuously
        │
        ▼
  YOLO model analyses each frame
  for violent behaviour patterns
        │
    ┌───┴───────────────────┐
    │ Violence NOT detected  │  Violence DETECTED
    │ → Continue monitoring  │        │
    └───────────────────────┘        ▼
                              📹 Flask records incident clip
                                      │
                                      ▼
                              ☁️ Clip uploaded to Firebase
                              Cloud Storage with timestamp
                                      │
                                      ▼
                              📲 Twilio fires SMS + Voice Call
                              to emergency contact numbers
                                      │
                                      ▼
                              📊 React dashboard updates
                              with live alert and clip link
```

---

## 🗂️ Project Structure

```
RiskVision/
│
├── Backend/                        # Python — Flask API + YOLO detection engine
│   ├── eye-view.py                 # Main application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── config/                     # Firebase & Twilio configuration helpers
│   ├── models/                     # YOLO model weights (.pt files)
│   └── eyeview-v2-firebase-adminsdk-*.json   # Firebase Admin SDK credentials
│
├── EyeView-frontend/               # React 19 + Vite 6 — live monitoring dashboard
│   ├── public/                     # Static assets and icons
│   └── src/
│       ├── components/             # Reusable UI — Alert cards, Video feed, Navbar
│       ├── pages/                  # Dashboard, Incident History, Settings, Login
│       ├── styles/                 # Global and component-level styles
│       └── utils/                  # Firebase client SDK, API helpers, formatters
│
├── Contributing.md                 # Contribution guidelines
├── Evaluator_QnA_Script.md         # Q&A script for project evaluators
├── Presentation_Guide.md           # Presentation walkthrough guide
├── project.md                      # Detailed project documentation
├── package.json                    # Root-level scripts & frontend dependencies
├── .gitignore
└── README.md
```

---

## 🧠 Tech Stack

**AI & Computer Vision (Backend)**
- [Python 3.8+](https://www.python.org/) — core backend language
- [Flask](https://flask.palletsprojects.com/) — lightweight API server streaming detection results
- [YOLO (Ultralytics)](https://ultralytics.com/) — real-time object & violence detection model
- [OpenCV](https://opencv.org/) — video frame capture, preprocessing, and clip recording

**Frontend Dashboard**
- [React 19](https://reactjs.org/) — latest stable React with concurrent features
- [Vite 6](https://vitejs.dev/) — blazing-fast dev server and build tool
- [Tailwind CSS 4](https://tailwindcss.com/) — utility-first responsive styling
- [Framer Motion](https://www.framer.com/motion/) — smooth animations and transitions
- [Axios](https://axios-http.com/) — HTTP client for backend API calls
- [React Router DOM 7](https://reactrouter.com/) — client-side routing
- [React Hot Toast](https://react-hot-toast.com/) — real-time alert toast notifications
- [React Icons](https://react-icons.github.io/react-icons/) — comprehensive icon library

**Cloud & Services**
- [Firebase 11](https://firebase.google.com/) — Cloud Storage for evidence clips + Authentication
- [Twilio](https://www.twilio.com/) — SMS and programmable voice call emergency alerts
- [Concurrently](https://www.npmjs.com/package/concurrently) — run frontend and backend simultaneously with a single command

---

## 🤖 YOLO Detection Engine

The core intelligence of RiskVision is a **YOLO (You Only Look Once)** deep learning model trained to identify violent human behaviour patterns in real time.

### How the Detection Works

1. **Frame Capture** — OpenCV reads continuous frames from the configured camera source (webcam, IP camera, or mobile stream)
2. **Inference** — Each frame is passed through the YOLO model which outputs bounding boxes and confidence scores for detected classes
3. **Threshold Filtering** — Only detections above a configurable confidence threshold trigger the alert pipeline (avoids false positives)
4. **Clip Recording** — OpenCV buffers the frames around the detection moment and saves them as a video clip
5. **Cooldown Period** — A configurable cooldown prevents repeated alerts for the same ongoing incident

### Model Configuration

The YOLO model weights (`.pt` file) are stored in `Backend/models/`. You can swap in any custom-trained YOLO model — for example a model fine-tuned on violence-specific datasets — by updating the model path in `eye-view.py`.

> 💡 **Using a Custom Model:** Train your model using [Ultralytics YOLO](https://docs.ultralytics.com/) on a violence detection dataset, export the `.pt` weights, and drop it into `Backend/models/`.

---

## 🔥 Firebase Integration

RiskVision uses Firebase for two critical functions: **Cloud Storage** for evidence clips and **Authentication** for dashboard access control.

### Firebase Cloud Storage

When violence is detected, the recorded clip is automatically uploaded to Firebase Cloud Storage with a timestamped filename. The React dashboard then fetches and displays these clips in the incident history log.

### Firebase Authentication

The monitoring dashboard is protected behind Firebase Authentication so only authorised operators can access live feeds and incident records.

### Setting Up Firebase

1. Go to [https://console.firebase.google.com/](https://console.firebase.google.com/) and create a new project
2. Enable **Cloud Storage** and **Authentication** (Email/Password or Google Sign-In) in the console
3. Go to **Project Settings → Service Accounts → Generate New Private Key** — download the JSON file
4. Rename the downloaded file and place it in the `Backend/` directory
5. In **Project Settings → General → Your Apps**, register a Web App and copy the Firebase config object
6. Add both sets of credentials to your `.env` files (see below)

> ⚠️ **The Firebase Admin SDK JSON file contains sensitive credentials. Never commit it to Git.** Add it to `.gitignore`.

---

## 📲 Twilio Alert System

When RiskVision detects a violent incident, **Twilio** immediately contacts configured emergency numbers through both SMS and automated voice calls — ensuring rapid response even when no one is watching the dashboard.

### Alert Behaviour

| Trigger | Alert Type | Recipient |
|---|---|---|
| Violence detected (first frame above threshold) | SMS with timestamp & location label | Admin / Authority number |
| Violence confirmed (clip recorded) | Voice call with automated message | Admin / Authority number |
| Detection cooldown expired + new incident | Both SMS and Voice Call repeated | Admin / Authority number |

### Setting Up Twilio

1. Create a free account at [https://www.twilio.com/](https://www.twilio.com/)
2. In the Twilio Console, note your **Account SID** and **Auth Token**
3. Get a **Twilio Phone Number** (free trial number works for testing)
4. Add all three values plus your target alert number to `Backend/.env`

> 💡 On a Twilio free trial account, you can only send alerts to **verified phone numbers**. Upgrade to a paid account for unrestricted alerting in production.

---

## ⚙️ Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm 9 or higher
- A webcam or IP camera feed
- A Firebase project (Storage + Authentication enabled)
- A Twilio account

### Step 1 — Clone the Repository

```bash
git clone https://github.com/Lucky-939/RiskVision.git
cd RiskVision
```

### Step 2 — Backend Setup

```bash
cd Backend

# Create a Python virtual environment
python -m venv venv

# Activate — Linux / macOS
source venv/bin/activate

# Activate — Windows (PowerShell)
.\venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt
```

### Step 3 — Place Firebase Admin SDK Credentials

Download your Firebase Admin SDK JSON key from the Firebase Console and place it in the `Backend/` directory. Update the filename reference in `eye-view.py` if needed.

### Step 4 — Frontend Setup

```bash
cd ../EyeView-frontend
npm install
```

### Step 5 — Configure Environment Variables

Create `.env` files for both backend and frontend (see [Environment Configuration](#-environment-configuration) below).

---

## 🔑 Environment Configuration

### Backend — `Backend/.env`

```env
# ── Twilio Emergency Alerts ───────────────────────────
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX        # Your Twilio number
ADMIN_PHONE_NUMBER=+91XXXXXXXXXX        # Alert recipient number

# ── Firebase Admin SDK ────────────────────────────────
FIREBASE_CREDENTIALS_PATH=./eyeview-v2-firebase-adminsdk-*.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# ── Detection Settings ────────────────────────────────
DETECTION_CONFIDENCE=0.65               # Confidence threshold (0.0 - 1.0)
ALERT_COOLDOWN_SECONDS=30               # Seconds between repeated alerts
CAMERA_SOURCE=0                         # 0 = default webcam, or IP camera URL
```

### Frontend — `EyeView-frontend/.env`

```env
# ── Firebase Web SDK ──────────────────────────────────
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_firebase_app_id

# ── Backend API ───────────────────────────────────────
VITE_API_BASE_URL=http://localhost:5000
```

> ⚠️ **Security Rules:**
> - Never commit `.env` files or the Firebase Admin SDK JSON to Git
> - Ensure both are listed in `.gitignore`
> - Use Firebase Storage Security Rules to restrict public access to evidence clips

---

## 🚀 Running the Application

### Option A — Run Everything with One Command (Recommended)

From the project root:

```bash
npm run start:all
```

This uses `concurrently` to start both the Flask backend and Vite frontend simultaneously.

### Option B — Run Separately

**Terminal 1 — Backend:**

```bash
cd Backend
source venv/bin/activate   # or .\venv\Scripts\activate on Windows
python eye-view.py
```

Backend runs at: **http://localhost:5000**

**Terminal 2 — Frontend:**

```bash
cd EyeView-frontend
npm run dev
```

Dashboard available at: **http://localhost:5173**

---

## 🐛 Troubleshooting

**Firebase credentials file not found**

Ensure the Admin SDK JSON file is in the `Backend/` directory and the path in `eye-view.py` matches the filename exactly. Run the backend from inside the `Backend/` folder so relative paths resolve correctly.

**Backend won't start**

Check that your virtual environment is activated, all packages are installed via `pip install -r requirements.txt`, and no other process is using port 5000. Verify Python version is 3.8 or higher with `python --version`.

**Camera not detected**

Set `CAMERA_SOURCE=0` in your `.env` for the default system webcam. For an IP camera, provide the RTSP stream URL (e.g., `rtsp://192.168.1.1:554/stream`). Ensure no other application is locking the camera.

**Frontend can't connect to backend**

Verify the backend is running on port 5000 and that `VITE_API_BASE_URL=http://localhost:5000` is set in `EyeView-frontend/.env`. Check that CORS is configured in `eye-view.py` to allow requests from `http://localhost:5173`.

**Twilio alerts not sending on free trial**

Free trial accounts can only send to verified numbers. Verify the recipient number in the Twilio Console under **Verified Caller IDs**, or upgrade to a paid account.

---

## 🛣️ Roadmap

- [ ] Multi-camera support — monitor multiple feeds simultaneously from one dashboard
- [ ] Advanced AI models — integrate more sophisticated pose estimation for improved accuracy
- [ ] Analytics dashboard — incident heatmaps, frequency trends, and response time reporting
- [ ] Mobile app — React Native app for field operators to receive and review alerts
- [ ] Email notifications — alongside Twilio SMS and voice alerts
- [ ] Enhanced security — role-based access control with multiple operator levels
- [ ] Kubernetes deployment — horizontal scaling for enterprise and smart city deployment
- [ ] Edge computing support — run YOLO inference on-device for reduced latency

---

## 🤝 Contributing

Contributions are welcome — especially improvements to detection accuracy, UI enhancements, and performance optimisation.

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/RiskVision.git

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes and commit
git add .
git commit -m "feat: describe your change here"

# 5. Push and open a Pull Request
git push origin feature/your-feature-name
```

### Guidelines

- Follow **PEP 8** for Python code and **ESLint** rules for JavaScript/React
- Use conventional commit messages (`feat:`, `fix:`, `docs:`, `perf:`)
- Comment all YOLO model configuration and detection threshold logic clearly
- Test on both webcam and IP camera sources before submitting a PR
- For major changes, open an issue first to discuss your approach
- See [Contributing.md](Contributing.md) for the full contribution guide

### 🐛 Reporting Issues

[Open an issue](https://github.com/Lucky-939/RiskVision/issues) with:
- A clear title and description of the problem
- Steps to reproduce it
- Your Python and Node.js versions
- Relevant error logs or screenshots

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

---

*Made with ❤️ for a safer world — [Lucky-939](https://github.com/Lucky-939)*
