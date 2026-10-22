# 🔌 RiskVision 2.0 — Beginner-Friendly Hardware Setup & Connection Guide

> **Hey there! 👋**  
> This guide is written so **anyone** can assemble and connect the hardware for **RiskVision 2.0** in under 20 minutes without needing any prior electronics experience!

---

## 📦 1. The 6 Items in Your Hardware Kit

Take out your components and identify them using this quick guide:

| Item | What It Looks Like | What It Does in RiskVision 2.0 |
| :--- | :--- | :--- |
| **1. ESP32-CAM Board** | Small rectangular board with an **OV2640 camera lens** attached via a golden ribbon cable. | Acts as **Camera 2** — streams live wireless video to the laptop over Wi-Fi. |
| **2. ESP32-CAM-MB Shield** | A base board of the exact same size, with a **Micro-USB port** and two female pin rows. | The programmer and power dock. Snaps onto the ESP32-CAM so you can plug it into your laptop with a USB cable. |
| **3. HC-SR501 PIR Sensor** | Green circuit board with a **round white plastic dome**. Has 3 pins on the bottom. | Detects human motion. Tells the laptop whether the room is occupied or empty. |
| **4. 5V Active Buzzer Module** | Small black cylinder mounted on a small blue/black PCB with **3 pins** (`VCC`, `GND`, `I/O` or `S`). | **Active Deterrence** — sounds a loud alarm to scare off attackers during high-severity (Tier 3) events. |
| **5. Half-Size Breadboard** | White plastic block with hundreds of tiny plug holes and `+` / `-` colored rails on the sides. | Lets you connect multiple wires together cleanly without cutting or soldering. |
| **6. Jumper Wires** | Colorful wires with pins on the ends (Male pins are pointy; Female ends are little sockets). | Connects all the sensors to the ESP32-CAM. |

---

## 🧩 2. Step 1: Snap the ESP32-CAM into the MB Shield

This is the easiest step!

1. Take the **ESP32-CAM** board and the **ESP32-CAM-MB** base shield.
2. Hold them so the **camera lens** is facing up, and the **Micro-USB port** is pointing **downwards / away from the camera lens**.
3. Align the two rows of metal pins on the ESP32-CAM into the two female sockets on the MB shield.
4. Gently press them together until they are firmly plugged in.
5. **That's it!** You can now plug a Micro-USB cable into the shield to power and program the board directly from your laptop.

---

## ⚡ 3. Step 2: Breadboard Power Connections

Because the ESP32-CAM only has **one 5V pin** and **one GND pin**, but both the **PIR sensor** and **Buzzer** need power, we share power using the breadboard's side rails:

1. Connect a jumper wire from **ESP32-CAM `5V` pin** $\rightarrow$ Breadboard **Red (+) Rail**.
2. Connect a jumper wire from **ESP32-CAM `GND` pin** $\rightarrow$ Breadboard **Blue (-) Rail**.

Now the entire Red rail is 5V, and the entire Blue rail is Ground (GND)!

---

## 🚶 Step 3: Connect the HC-SR501 PIR Motion Sensor

Look at the 3 pins on the PIR motion sensor (remove the white plastic dome briefly if you need to see the labels: `VCC`, `OUT`, `GND`):

```
PIR Sensor Pin                Where to Connect It
─────────────────────────────────────────────────────────────
VCC (Power)            ---->  Breadboard Red (+) Rail (5V)
GND (Ground)           ---->  Breadboard Blue (-) Rail (GND)
OUT (Digital Signal)   ---->  ESP32-CAM GPIO 13 (Pin labeled "13" or "IO13")
```

> 💡 **Tuning the PIR Sensor:**  
> The PIR board has two tiny orange screws (potentiometers):
> - **Sensitivity (Distance):** Turn gently clockwise to detect up to 7 meters.
> - **Time Delay:** Turn fully counter-clockwise so it resets quickly for fast testing!

---

## 🔊 Step 4: Connect the 5V Active Buzzer Module

Look at the 3 pins on your buzzer module (labeled `VCC`, `GND`, and `I/O` or `S`):

```
Buzzer Module Pin             Where to Connect It
─────────────────────────────────────────────────────────────
VCC (Power)            ---->  Breadboard Red (+) Rail (5V)
GND (Ground)           ---->  Breadboard Blue (-) Rail (GND)
I/O or S (Signal)      ---->  ESP32-CAM GPIO 14 (Pin labeled "14" or "IO14")
```

When RiskVision detects a weapon or violent assault, the software tells the ESP32 to set **GPIO 14 to HIGH (3.3V)**, which instantly triggers the onboard transistor and sounds the buzzer loud and clear!

---

## 📋 Complete Wiring Master Sheet

Keep this table in front of you while plugging in the wires:

| Component | Pin Label | Wire Color (Suggested) | Destination Pin |
| :--- | :--- | :--- | :--- |
| **ESP32-CAM** | `5V` | 🔴 Red | Breadboard **Red (+) Rail** |
| **ESP32-CAM** | `GND` | ⚫ Black | Breadboard **Blue (-) Rail** |
| **PIR Motion Sensor** | `VCC` | 🔴 Red | Breadboard **Red (+) Rail** |
| **PIR Motion Sensor** | `GND` | ⚫ Black | Breadboard **Blue (-) Rail** |
| **PIR Motion Sensor** | `OUT` | 🟡 Yellow | **ESP32-CAM GPIO 13** |
| **Active Buzzer Module** | `VCC` | 🔴 Red | Breadboard **Red (+) Rail** |
| **Active Buzzer Module** | `GND` | ⚫ Black | Breadboard **Blue (-) Rail** |
| **Active Buzzer Module** | `I/O` or `S` | 🟠 Orange | **ESP32-CAM GPIO 14** |

---

## 💻 5. Arduino IDE Setup (How to Flash Code)

Follow these 4 simple steps to upload the code to the ESP32-CAM:

### 1. Install Arduino IDE
* Download and install the latest **Arduino IDE** from [arduino.cc](https://www.arduino.cc/en/software).

### 2. Add ESP32 Board Support
* Open Arduino IDE $\rightarrow$ Go to **File** $\rightarrow$ **Preferences**.
* In **Additional boards manager URLs**, paste this link:
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
* Go to **Tools** $\rightarrow$ **Board** $\rightarrow$ **Boards Manager**.
* Search for `esp32` by Espressif Systems and click **Install**.

### 3. Select Board Settings in Arduino IDE
* **Board:** `Tools` $\rightarrow$ `Board` $\rightarrow$ `esp32` $\rightarrow$ Select **"AI Thinker ESP32-CAM"**.
* **Port:** `Tools` $\rightarrow$ `Port` $\rightarrow$ Select the **COM port** of your plugged-in USB cable (e.g., `COM3`, `COM4`).
* **Upload Speed:** `115200`
* **Flash Frequency:** `40MHz`

---

## 📜 6. The Complete Arduino Code to Copy & Paste

Create a new sketch in Arduino IDE, paste the code below, replace your **Wi-Fi Name & Password**, and click **Upload (Arrow button)**:

```cpp
/*
 * RiskVision 2.0 - ESP32-CAM IoT Node Firmware
 * Features:
 * 1. OV2640 Wi-Fi Video Stream Server (Port 81)
 * 2. HC-SR501 PIR Motion Sensor on GPIO 13
 * 3. Active Deterrence Buzzer on GPIO 14
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// ==========================================
// 1. YOUR WI-FI CREDENTIALS (REPLACE THESE!)
// ==========================================
const char* ssid     = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ==========================================
// 2. PIN DEFINITIONS
// ==========================================
#define PIR_PIN    13  // Motion Sensor Input
#define BUZZER_PIN 14  // Active Buzzer Output

// AI-Thinker Camera Pin Configuration
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

WiFiServer streamServer(81);
WebServer controlServer(80);

void startCameraServer() {
  streamServer.begin();
  
  // API endpoints for control
  controlServer.on("/buzzer/on", []() {
    digitalWrite(BUZZER_PIN, HIGH);
    controlServer.send(200, "application/json", "{\"buzzer\": true}");
  });

  controlServer.on("/buzzer/off", []() {
    digitalWrite(BUZZER_PIN, LOW);
    controlServer.send(200, "application/json", "{\"buzzer\": false}");
  });

  controlServer.on("/status", []() {
    int motion = digitalRead(PIR_PIN);
    String json = "{\"motion\": " + String(motion == HIGH ? "true" : "false") + "}";
    controlServer.send(200, "application/json", json);
  });

  controlServer.begin();
}

void handleStreamClient() {
  WiFiClient client = streamServer.available();
  if (!client) return;

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println("");

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) break;

    client.println("--frame");
    client.println("Content-Type: image/jpeg");
    client.println("Content-Length: " + String(fb->len));
    client.println("");
    client.write(fb->buf, fb->len);
    client.println("");
    
    esp_camera_fb_return(fb);
    controlServer.handleClient();
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Beep once on startup
  digitalWrite(BUZZER_PIN, HIGH);
  delay(150);
  digitalWrite(BUZZER_PIN, LOW);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;    // 640x480
  config.jpeg_quality = 12;
  config.fb_count = 2;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  // Connect to Wi-Fi
  Serial.printf("\nConnecting to %s...", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n>>> WiFi Connected! <<<");
  Serial.print("ESP32-CAM Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81/stream");

  startCameraServer();
}

void loop() {
  handleStreamClient();
  controlServer.handleClient();
}
```

---

## 🔗 7. Connecting Hardware to the Web Software (Final Step)

Once the code is uploaded:
1. Open the **Arduino Serial Monitor** (set baud rate to **`115200`**).
2. Press the small **RST (Reset)** button on the ESP32-CAM-MB shield.
3. You will see its Wi-Fi IP address printed, for example:
   ```
   >>> WiFi Connected! <<<
   ESP32-CAM Stream URL: http://192.168.1.150:81/stream
   ```
4. Open your RiskVision web dashboard (**`http://localhost:5173`**).
5. Click the **"⚙️ ESP32 Node"** button in the top right.
6. Paste the URL: `http://192.168.1.150:81/stream` and click **Save & Connect**.
7. **BAM!** Camera 2 will immediately light up with live video from your wireless ESP32 camera, tracking suspects across views with Person Re-ID and sounding the buzzer on high alerts! 🎉

---

## ❓ Troubleshooting & Beginner Tips

* **Issue: "Camera init failed with error 0x20001"**
  * *Solution:* Check the camera ribbon connector. Ensure the gold pins are pressed flat and the small black clamp is snapped shut.
* **Issue: Arduino upload hangs on "Connecting........____"**
  * *Solution:* Make sure the ESP32-CAM is pushed completely into the MB shield sockets. When flashing starts, press the **RST** button on the shield once.
* **Issue: Board resets continuously**
  * *Solution:* Use a quality USB data cable plugged into a high-power USB port on your laptop, or use a 5V phone charger adapter.
