# 🎤 RiskVision - Project Presentation Script

> [!TIP]
> **Pro Tip for Tomorrow:** Read this script a few times tonight. During the live demo, use a clear, slow striking motion with a larger object (like a toy knife or stick) under good lighting to ensure the YOLO AI detects the action without motion blur!

---

## 1. Introduction (2 Minutes)

**"Good morning/afternoon everyone. Today, I am excited to present our project: RiskVision."**

"Traditional surveillance systems are completely passive—they only record crimes *as* they happen, which means security personnel can only review the footage *after* the damage is done. We asked ourselves: *'What if cameras could actively understand what they are seeing and stop incidents before they escalate?'*"

"That is exactly what RiskVision does. It is an active, AI-powered surveillance system that detects violence in real-time, automatically records the incident, and instantly notifies administrators so they can take immediate action."

---

## 2. The Technology Stack (2 Minutes)

"To build a system this robust, we engineered a modern, full-stack architecture using industry-standard tools:"

### 🧠 The AI & Computer Vision (The Brain)
*   **Ultralytics YOLO (You Only Look Once):** We use a custom-trained YOLO model for lightning-fast object and action detection. It analyzes frames in milliseconds to detect violent postures or weapons.
*   **OpenCV:** We use OpenCV to capture live video streams, process frames, and draw real-time bounding boxes with confidence scores.

### ⚙️ The Backend (The Engine)
*   **Python & Flask:** Our backend server is built on Flask. It acts as the bridge between the AI model and the frontend, processing video frames and managing secure API routes.
*   **JWT (JSON Web Tokens):** Ensures that our backend API and user dashboards are securely authenticated.
*   **ImageIO:** Replaced standard FFmpeg dependencies to seamlessly encode and compress recorded incidents into high-quality MP4 files entirely in Python.

### ☁️ Cloud & Communications
*   **Supabase (PostgreSQL & Storage):** Instead of saving data locally, we migrated to Supabase. All security alerts are logged in a highly scalable Postgres database, and the video clips are securely uploaded to a Supabase Storage CDN for instant global access.
*   **Twilio API:** The moment violence is detected, our backend triggers the Twilio API to fire off an emergency SMS directly to the administrator's phone.

### 💻 The Frontend (The Dashboard)
*   **React + Vite:** We built a blazing-fast, single-page application dashboard.
*   **Tailwind CSS & Framer Motion:** To give the dashboard a premium, modern feel with dynamic animations and fully responsive UI components.

---

## 3. Live Demonstration (3-4 Minutes)

> [!IMPORTANT]
> **Action:** Open the React Dashboard and log in.

"Let me show you how it works in practice. This is the RiskVision command center."

**[Show Live Monitoring]**
"Here you can see the live feed. The YOLO model is actively scanning every single frame. Notice how it marks 'Non-violence' in green."

**[Trigger the Alert]**
"Now, I will simulate a violent action."
*(Make your deliberate, clear striking motion in front of the camera)*

**[Explain the Workflow]**
"As you can see, the AI instantly detected the action. Behind the scenes, three things just happened simultaneously:"
1.  "A 10-second video clip of the incident was captured, converted to an MP4, and uploaded to our Supabase Cloud Storage."
2.  "The alert metadata—including the timestamp, AI confidence score, and my estimated location—was saved to our Supabase Database."
3.  "And right now..." *(Hold up your phone)* "...I just received a live SMS from Twilio warning me of the incident."

**[Show the Alerts & History Tabs]**
"If I navigate to the **Alerts** tab, you can see the incident logged. Because we use Supabase CDN, the video plays instantly right here in the browser. Administrators can review the footage and even use the new 'Delete' feature to clear the incident from the cloud once it is resolved."

---

## 4. Addressing Hardware Limitations (1 Minute)

"You might wonder about accuracy. For this demonstration, we are using a standard laptop webcam. Webcams suffer from low shutter speeds, which introduces heavy motion blur during fast movements—temporarily blinding the AI. 

However, in a real-world deployment, RiskVision would be hooked up to 60FPS, high-shutter-speed CCTV cameras. By eliminating motion blur, our AI model achieves near-perfect accuracy even during the fastest, most chaotic incidents."

---

## 5. Conclusion (1 Minute)

"In conclusion, RiskVision bridges the gap between passive recording and active prevention. By combining advanced computer vision with cloud infrastructure and instant communications, we've built a scalable security solution for the modern world."

"Thank you. I'd be happy to answer any questions."
