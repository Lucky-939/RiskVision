import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { FaExclamationTriangle, FaMapMarkerAlt, FaClock, FaSync, FaPlay, FaVideo, FaBell, FaTrash } from "react-icons/fa";
import axios from 'axios';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [videoErrors, setVideoErrors] = useState(new Set());

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://localhost:5000/alerts");
      const sortedAlerts = (response.data.alerts || []).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      setAlerts(sortedAlerts);
    } catch (err) {
      console.error("Error fetching alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!id || !window.confirm("Are you sure you want to delete this alert? It will also be removed from history.")) return;
    try {
      await axios.delete(`http://localhost:5000/alerts/${id}`);
      setAlerts(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      console.error("Error deleting alert:", err);
      alert("Failed to delete alert");
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex justify-between items-center mb-12"
        >
          <div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-red-400 via-orange-500 to-yellow-500 bg-clip-text text-transparent mb-4">
              Security Alerts
            </h1>
            <p className="text-gray-400 text-lg">Real-time incident monitoring and response system</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchAlerts}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-2xl font-medium transition-all duration-300 flex items-center gap-3 shadow-lg disabled:opacity-50"
            disabled={loading}
          >
            <FaSync className={loading ? "animate-spin" : ""} />
            {loading ? "Refreshing..." : "Refresh Alerts"}
          </motion.button>
        </motion.div>

        {loading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20"
          >
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-gray-400 text-lg">Loading security alerts...</p>
          </motion.div>
        ) : alerts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <FaBell className="text-gray-600 text-3xl" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-400 mb-2">All Clear</h3>
            <p className="text-gray-500">No security alerts detected. System is monitoring actively.</p>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8"
          >
            {alerts.map((alert, index) => {
              const readableTime = new Date(alert.timestamp).toLocaleString();

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ scale: 1.02, y: -5 }}
                  className={`bg-gradient-to-br from-gray-800 to-gray-700 rounded-2xl p-6 shadow-2xl border transition-all duration-300 overflow-hidden ${
                    alert.tier === 3
                      ? "border-red-500/50 hover:border-red-400"
                      : alert.tier === 2
                      ? "border-orange-500/50 hover:border-orange-400"
                      : "border-blue-500/40 hover:border-blue-400"
                  }`}
                >
                  {/* Alert Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-xl ${
                        alert.tier === 3 ? "bg-red-500/20 text-red-400" : alert.tier === 2 ? "bg-orange-500/20 text-orange-400" : "bg-blue-500/20 text-blue-400"
                      }`}>
                        <FaExclamationTriangle className="text-xl" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="text-xl font-bold text-white">
                            {alert.alert_type || "Threat Detected"}
                          </h3>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                            alert.tier === 3 ? "bg-red-500/30 text-red-300 border border-red-500/40" : alert.tier === 2 ? "bg-orange-500/30 text-orange-300 border border-orange-500/40" : "bg-blue-500/30 text-blue-300 border border-blue-500/40"
                          }`}>
                            TIER {alert.tier || 1}: {alert.tier_label || "ALERT"}
                          </span>
                          {alert.suspect_id && alert.suspect_id !== "N/A" && (
                            <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 font-semibold">
                              {alert.suspect_id}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    {alert.id && (
                      <button
                        onClick={() => handleDelete(alert.id)}
                        className="text-gray-400 hover:text-red-500 transition-colors p-2 bg-gray-700/50 hover:bg-gray-700 rounded-lg"
                        title="Delete Alert"
                      >
                        <FaTrash />
                      </button>
                    )}
                  </div>

                  {/* Alert Details */}
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-3 text-gray-300">
                      <FaClock className="text-blue-400 flex-shrink-0" />
                      <span className="text-sm">{readableTime}</span>
                    </div>

                    <div className="flex items-center gap-3 text-gray-300">
                      <FaMapMarkerAlt className="text-green-400 flex-shrink-0" />
                      <span className="text-sm">{alert.location || "Unknown Location"}</span>
                    </div>

                    {alert.confidence !== undefined && (
                      <div className="flex items-center gap-3">
                        <div className="text-gray-300 text-sm font-medium">Threat Score:</div>
                        <div className="flex-1 bg-gray-600 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-500 ${
                              alert.tier === 3 ? "bg-gradient-to-r from-orange-500 to-red-500" : "bg-gradient-to-r from-blue-400 to-yellow-400"
                            }`}
                            style={{ width: `${(alert.confidence <= 1.0 ? alert.confidence * 100 : alert.confidence)}%` }}
                          ></div>
                        </div>
                        <span className="text-white text-sm font-bold">
                          {(alert.confidence <= 1.0 ? alert.confidence * 100 : alert.confidence).toFixed(0)}%
                        </span>
                      </div>
                    )}

                    {alert.audio_confidence !== undefined && alert.audio_confidence > 0 && (
                      <div className="text-xs text-blue-300 flex items-center justify-between bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20">
                        <span>Acoustic Distress Confirmed:</span>
                        <span className="font-bold">{(alert.audio_confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>

                  {/* Video Section */}
                  {alert.video_url && !videoErrors.has(alert.video_url) && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="relative group"
                    >
                      <video
                        className="w-full h-32 object-cover rounded-xl border border-gray-600 group-hover:border-blue-400 transition-colors"
                        controls
                        src={alert.video_url}
                        poster="/api/placeholder/400/200"
                        preload="none"
                        onError={(e) => {
                          console.error(`Error loading video: ${alert.video_url}`, e.target.error);
                          setVideoErrors(prev => new Set([...prev, alert.video_url]));
                        }}
                      >
                        Your browser does not support the video tag.
                      </video>
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 rounded-xl flex items-center justify-center">
                        <FaPlay className="text-white/0 group-hover:text-white/80 text-2xl transition-all duration-300" />
                      </div>
                    </motion.div>
                  )}

                  {/* Video Error Section */}
                  {alert.video_url && videoErrors.has(alert.video_url) && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="relative bg-gradient-to-br from-gray-700 to-gray-600 rounded-xl border border-red-500/30 p-4 flex items-center gap-3"
                    >
                      <div className="w-10 h-10 bg-red-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <FaVideo className="text-red-400 text-lg" />
                      </div>
                      <div>
                        <p className="text-red-400 text-sm font-medium">Video Corrupted</p>
                        <p className="text-gray-400 text-xs">Recording failed during capture</p>
                      </div>
                    </motion.div>
                  )}

                  {/* Action Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      if (alert.video_url && !videoErrors.has(alert.video_url)) {
                        window.open(alert.video_url, '_blank');
                      }
                    }}
                    className={`w-full mt-4 py-3 px-4 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
                      !alert.video_url || videoErrors.has(alert.video_url)
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white'
                    }`}
                    disabled={!alert.video_url || videoErrors.has(alert.video_url)}
                  >
                    <FaVideo />
                    {videoErrors.has(alert.video_url) ? 'Video Unavailable' : 'View Full Incident'}
                  </motion.button>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
