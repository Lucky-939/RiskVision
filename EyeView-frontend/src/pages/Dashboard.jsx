import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import {
  FaPlay,
  FaPause,
  FaExpand,
  FaCompress,
  FaEye,
  FaBell,
  FaVideo,
  FaClock,
  FaShieldAlt,
  FaExclamationTriangle,
  FaMicrophone,
  FaWalking,
  FaBullhorn,
  FaUserSecret,
  FaCog
} from "react-icons/fa";
import axios from "axios";

const Dashboard = () => {
  const [pausedStates, setPausedStates] = useState({});
  const [fullscreenStates, setFullscreenStates] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [telemetry, setTelemetry] = useState(null);
  const [buzzerTriggering, setBuzzerTriggering] = useState(false);
  const [camera2Url, setCamera2Url] = useState("");
  const [showConfigModal, setShowConfigModal] = useState(false);
  
  const videoRefs = useRef({});

  // Poll alerts and real-time telemetry
  useEffect(() => {
    fetchAlerts();
    fetchTelemetry();

    const telemetryInterval = setInterval(fetchTelemetry, 1000); // 1-second telemetry refresh
    const alertInterval = setInterval(fetchAlerts, 4000);

    return () => {
      clearInterval(telemetryInterval);
      clearInterval(alertInterval);
    };
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get("http://localhost:5000/alerts");
      setAlerts((response.data.alerts || []).slice(0, 5));
    } catch (error) {
      console.error("Failed to fetch alerts:", error);
    }
  };

  const fetchTelemetry = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/telemetry");
      setTelemetry(response.data);
    } catch (error) {
      // Backend may be offline or starting up
    }
  };

  const togglePause = (id, src) => {
    const isPaused = pausedStates[id] || false;
    const updatedPaused = { ...pausedStates, [id]: !isPaused };

    if (videoRefs.current[id]) {
      videoRefs.current[id].src = isPaused ? src : "";
    }
    setPausedStates(updatedPaused);
  };

  const toggleFullscreen = (id) => {
    const isFullscreen = fullscreenStates[id] || false;
    const updatedFullscreen = { ...fullscreenStates, [id]: !isFullscreen };

    const el = videoRefs.current[id];
    if (!el) return;

    if (!document.fullscreenElement) {
      el.requestFullscreen().catch((err) => console.error("Fullscreen error:", err));
    } else {
      document.exitFullscreen();
    }
    setFullscreenStates(updatedFullscreen);
  };

  const handleTriggerBuzzer = async () => {
    try {
      setBuzzerTriggering(true);
      await axios.post("http://localhost:5000/api/actuator/buzzer");
      setTimeout(() => setBuzzerTriggering(false), 2000);
    } catch (err) {
      console.error("Buzzer trigger failed:", err);
      setBuzzerTriggering(false);
    }
  };

  const handleTogglePIR = async () => {
    try {
      const currentMotion = telemetry?.iot?.motion_detected ?? true;
      await axios.post("http://localhost:5000/api/sensor/pir", { motion: !currentMotion });
      fetchTelemetry();
    } catch (err) {
      console.error("PIR toggle failed:", err);
    }
  };

  const handleSaveCamera2Url = async (e) => {
    e.preventDefault();
    if (!camera2Url) return;
    try {
      await axios.post("http://localhost:5000/api/config/camera2", { url: camera2Url });
      setShowConfigModal(false);
      // Reload stream
      if (videoRefs.current[2]) {
        videoRefs.current[2].src = `http://localhost:5000/video_feed/cam2?t=${Date.now()}`;
      }
    } catch (err) {
      alert("Failed to update Camera 2 URL");
    }
  };

  // Derive status badge colors
  const currentTier = telemetry?.fusion?.current_tier || 0;
  const tierColor =
    currentTier === 3
      ? "bg-red-500/20 text-red-400 border-red-500/40"
      : currentTier === 2
      ? "bg-orange-500/20 text-orange-400 border-orange-500/40"
      : currentTier === 1
      ? "bg-blue-500/20 text-blue-400 border-blue-500/40"
      : "bg-green-500/20 text-green-400 border-green-500/40";

  const audioConf = telemetry?.audio?.distress_confidence || 0;
  const audioPercentage = Math.min(100, Math.round(audioConf * 100));
  const pirActive = telemetry?.iot?.motion_detected ?? true;

  const cameras = [
    {
      id: 1,
      name: "Camera 1: Primary Controller (Webcam)",
      badge: "YOLOv11 + Weapon + Audio Fusion",
      src: "http://localhost:5000/video_feed/cam1"
    },
    {
      id: 2,
      name: "Camera 2: IoT Node (ESP32-CAM)",
      badge: "Cross-Camera Person Re-ID Node",
      src: "http://localhost:5000/video_feed/cam2"
    }
  ];

  return (
    <div className="bg-gray-900 min-h-screen text-white w-full p-6">
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        
        {/* Top Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-4xl font-extrabold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent">
                RiskVision 2.0 Command Center
              </h1>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${tierColor}`}>
                {currentTier > 0 ? `TIER ${currentTier}: ${telemetry?.fusion?.tier_label}` : "SYSTEM NORMAL"}
              </span>
            </div>
            <p className="text-gray-400 text-sm mt-1">
              Multimodal AI Violence Detection, Acoustic Distress & Active Deterrence
            </p>
          </div>

          {/* Quick Actuator Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleTriggerBuzzer}
              disabled={buzzerTriggering}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all shadow-lg ${
                buzzerTriggering || telemetry?.fusion?.buzzer_active
                  ? "bg-red-600 text-white animate-bounce"
                  : "bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40"
              }`}
              title="Test Active Deterrence Buzzer"
            >
              <FaBullhorn className={buzzerTriggering ? "animate-spin" : ""} />
              {buzzerTriggering || telemetry?.fusion?.buzzer_active ? "Buzzer Sounding!" : "Test Siren"}
            </button>

            <button
              onClick={() => setShowConfigModal(true)}
              className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm border border-gray-700 transition-colors"
              title="Configure Camera 2 ESP32 IP"
            >
              <FaCog /> ESP32 Node
            </button>
          </div>
        </div>

        {/* Real-time Telemetry Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          
          {/* Multimodal Risk Card */}
          <div className="bg-gray-800/80 p-5 rounded-xl border border-gray-700/60 shadow-lg backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Unified Threat Score</p>
                <p className="text-2xl font-bold mt-1 text-white">
                  {(telemetry?.fusion?.fused_score ? telemetry.fusion.fused_score * 100 : 0).toFixed(0)}%
                </p>
              </div>
              <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400 text-xl">
                <FaShieldAlt />
              </div>
            </div>
            <div className="mt-3 bg-gray-700 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  currentTier === 3 ? "bg-red-500" : currentTier === 2 ? "bg-orange-400" : "bg-blue-400"
                }`}
                style={{ width: `${Math.min(100, (telemetry?.fusion?.fused_score || 0) * 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Audio Distress Meter Card */}
          <div className="bg-gray-800/80 p-5 rounded-xl border border-gray-700/60 shadow-lg backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Live Mic & Distress</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className={`text-2xl font-bold ${audioPercentage > 45 ? "text-red-400" : "text-gray-200"}`}>
                    {telemetry?.audio?.mic_level !== undefined ? `${Math.round(telemetry.audio.mic_level)}%` : "0%"}
                  </p>
                  <span className="text-xs text-gray-400">
                    Scream: <b className={audioPercentage > 45 ? "text-red-400 font-bold" : "text-yellow-400"}>{audioPercentage}%</b>
                  </span>
                </div>
              </div>
              <div className={`p-3 rounded-xl text-xl ${audioPercentage > 45 ? "bg-red-500/20 text-red-400 animate-pulse" : "bg-blue-500/10 text-blue-400"}`}>
                <FaMicrophone />
              </div>
            </div>
            <div className="mt-3 bg-gray-700 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full transition-all duration-150 ${
                  audioPercentage > 45 ? "bg-red-500" : (telemetry?.audio?.mic_level || 0) > 25 ? "bg-yellow-400" : "bg-emerald-400"
                }`}
                style={{ width: `${Math.max(4, Math.min(100, telemetry?.audio?.mic_level || 0))}%` }}
              ></div>
            </div>
          </div>

          {/* PIR Motion & Gating Card */}
          <div
            onClick={handleTogglePIR}
            className="bg-gray-800/80 p-5 rounded-xl border border-gray-700/60 shadow-lg backdrop-blur cursor-pointer hover:border-emerald-500/40 transition-colors"
            title="Click to toggle simulated motion state"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">PIR Motion Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-2.5 h-2.5 rounded-full ${pirActive ? "bg-emerald-400 animate-pulse" : "bg-gray-500"}`}></div>
                  <p className="text-lg font-bold text-white">
                    {pirActive ? "Motion Detected" : "Power Saver"}
                  </p>
                </div>
              </div>
              <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-xl">
                <FaWalking />
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Mode: {telemetry?.iot?.inference_mode || "PIR_BURST"} (Click to toggle)
            </p>
          </div>

          {/* Suspect Tracking / Person Re-ID Card */}
          <div className="bg-gray-800/80 p-5 rounded-xl border border-gray-700/60 shadow-lg backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Suspect Re-ID Active</p>
                <p className="text-2xl font-bold mt-1 text-white">
                  {telemetry?.suspects?.length || 0} Suspects
                </p>
              </div>
              <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl text-yellow-400 text-xl">
                <FaUserSecret />
              </div>
            </div>
            <p className="text-xs text-gray-400 mt-2 truncate">
              {telemetry?.suspects?.length
                ? `Tracking: ${telemetry.suspects.map((s) => s.id).join(", ")}`
                : "No active cross-camera targets"}
            </p>
          </div>
        </div>

        {/* Main Section: Dual Video Stream Grid & Alerts Column */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Dual Camera Stream Grid (2 Columns) */}
          <div className="xl:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold flex items-center gap-2 text-gray-100">
                <FaVideo className="text-blue-400" /> Multi-Camera Live Network
              </h2>
              <span className="text-xs bg-gray-800 border border-gray-700 px-3 py-1 rounded-full text-gray-300">
                Dual Node Feed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {cameras.map((cam) => (
                <div
                  key={cam.id}
                  className="bg-gray-800/90 rounded-2xl overflow-hidden border border-gray-700/80 shadow-2xl flex flex-col justify-between"
                >
                  <div className="relative bg-black h-64 md:h-72 flex items-center justify-center">
                    <img
                      ref={(el) => (videoRefs.current[cam.id] = el)}
                      src={cam.src}
                      alt={cam.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback if camera stream drops
                        e.target.onerror = null;
                      }}
                    />

                    {/* Camera Control Overlay */}
                    <div className="absolute top-3 right-3 flex items-center gap-2">
                      <button
                        onClick={() => togglePause(cam.id, cam.src)}
                        className="p-2 bg-black/60 hover:bg-black/90 text-white rounded-lg transition-colors backdrop-blur text-sm"
                        title={pausedStates[cam.id] ? "Resume Stream" : "Pause Stream"}
                      >
                        {pausedStates[cam.id] ? <FaPlay /> : <FaPause />}
                      </button>
                      <button
                        onClick={() => toggleFullscreen(cam.id)}
                        className="p-2 bg-black/60 hover:bg-black/90 text-white rounded-lg transition-colors backdrop-blur text-sm"
                        title="Fullscreen"
                      >
                        {fullscreenStates[cam.id] ? <FaCompress /> : <FaExpand />}
                      </button>
                    </div>

                    {/* Live Stream Status Tag */}
                    <div className="absolute bottom-3 left-3 flex items-center gap-2 bg-black/60 backdrop-blur px-2.5 py-1 rounded-md text-xs">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                      <span className="font-medium text-gray-200">LIVE FEED</span>
                    </div>
                  </div>

                  {/* Camera Details Footer */}
                  <div className="p-4 border-t border-gray-700/60 bg-gray-800/40">
                    <h3 className="text-sm font-semibold text-gray-200">{cam.name}</h3>
                    <p className="text-xs text-gray-400 mt-1">{cam.badge}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Incident Feed Sidebar */}
          <div className="xl:col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold flex items-center gap-2 text-gray-100">
                <FaExclamationTriangle className="text-red-400" /> Incident Stream
              </h2>
              <button
                onClick={fetchAlerts}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors font-medium"
              >
                Refresh
              </button>
            </div>

            <div className="space-y-3">
              {alerts.length > 0 ? (
                alerts.map((alert, index) => {
                  const tier = alert.tier || 1;
                  const border =
                    tier === 3
                      ? "border-red-500/40 bg-red-500/5"
                      : tier === 2
                      ? "border-orange-500/40 bg-orange-500/5"
                      : "border-blue-500/40 bg-blue-500/5";
                  const badge =
                    tier === 3
                      ? "bg-red-500/20 text-red-400"
                      : tier === 2
                      ? "bg-orange-500/20 text-orange-400"
                      : "bg-blue-500/20 text-blue-400";

                  return (
                    <motion.div
                      key={alert.id || index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`p-4 rounded-xl border ${border} bg-gray-800/80 transition-all`}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${badge}`}>
                          TIER {tier}: {alert.tier_label || "ALERT"}
                        </span>
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <FaClock size={10} /> {alert.timestamp?.split(" ")[1] || "Just now"}
                        </span>
                      </div>

                      <p className="text-sm font-semibold text-gray-200 mt-2">
                        {alert.alert_type || "Threat Detected"}
                      </p>

                      <div className="flex items-center justify-between text-xs text-gray-400 mt-2">
                        <span>Confidence: <b>{((alert.confidence || 0) * 100).toFixed(0)}%</b></span>
                        <span className="truncate max-w-[140px] text-gray-500">{alert.location || "Local"}</span>
                      </div>
                    </motion.div>
                  );
                })
              ) : (
                <div className="bg-gray-800/60 p-8 rounded-xl border border-gray-700/60 text-center text-gray-400">
                  <FaBell className="text-3xl mx-auto mb-2 text-gray-600" />
                  <p className="text-sm font-medium">All Clear</p>
                  <p className="text-xs text-gray-500 mt-1">Multi-sensor fusion monitoring continuously.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal: ESP32-CAM Stream URL Configuration */}
        {showConfigModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-800 border border-gray-700 rounded-2xl p-6 max-w-md w-full shadow-2xl">
              <h3 className="text-lg font-bold text-white mb-2">Configure Camera 2 (ESP32-CAM)</h3>
              <p className="text-xs text-gray-400 mb-4">
                Enter the local Wi-Fi IP stream URL printed in your Arduino Serial Monitor (e.g. <code>http://192.168.1.150:81/stream</code>) or leave blank for local video loopback.
              </p>

              <form onSubmit={handleSaveCamera2Url} className="space-y-4">
                <input
                  type="text"
                  placeholder="http://192.168.1.xxx:81/stream"
                  value={camera2Url}
                  onChange={(e) => setCamera2Url(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />

                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowConfigModal(false)}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-xl text-sm text-gray-300"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-medium text-white shadow-lg"
                  >
                    Save & Connect
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Dashboard;
