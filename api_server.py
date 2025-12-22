#!/usr/bin/env python3
"""
Flask API Server for Fish Monitoring System
Provides REST API and video streaming endpoints
"""

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime
import logging

from camera_handler import CameraHandler
from fish_detector import FishDetector
from behavior_analyzer import BehaviorAnalyzer
from rainfall_detector import RainfallDetector
from alert_system import AlertSystem
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global system instance
system = None


class FishMonitoringSystem:
    def __init__(self):
        """Initialize the fish monitoring system"""
        logger.info("Initializing Fish Monitoring System for API...")
        
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.fish_detector = FishDetector(self.config)
        self.behavior_analyzer = BehaviorAnalyzer(self.config)
        self.rainfall_detector = RainfallDetector(self.config)
        self.alert_system = AlertSystem(self.config)
        
        self.running = False
        self.monitoring_thread = None
        self.last_detection_time = None
        self.last_alert_summary = None
        self.pond_status = 'normal'  # normal, warning, critical
        
        logger.info("System initialized successfully")
    
    def start(self):
        """Start the monitoring system"""
        logger.info("Starting monitoring system...")
        self.running = True
        
        # Start camera
        self.camera.start()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_fish)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop the monitoring system"""
        logger.info("Stopping monitoring system...")
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.camera.stop()
        logger.info("Monitoring system stopped")
    
    def _monitor_fish(self):
        """Background fish monitoring loop"""
        while self.running:
            try:
                # Capture frame
                frame = self.camera.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Run detection
                detections = self.fish_detector.detect(frame)
                
                if detections and len(detections) > 0:
                    self.last_detection_time = datetime.now().isoformat()
                    
                    # Analyze behavior (using correct method name: analyze, not analyze_frame)
                    analysis = self.behavior_analyzer.analyze(frame, detections, 0)
                    
                    # Check for alerts
                    if analysis:
                        for fish_id, behavior in analysis.items():
                            if behavior.get('is_side_floating', False):
                                self.pond_status = 'critical'
                                self.last_alert_summary = 'Possible mortality detected - side floating'
                                break
                            elif behavior.get('movement_score', 1.0) < 0.3:
                                self.pond_status = 'warning'
                                self.last_alert_summary = 'Abnormal behavior detected - low movement'
                            else:
                                self.pond_status = 'normal'
                                self.last_alert_summary = None
                
                time.sleep(1 / self.config.FRAME_RATE)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)


def generate_frames(camera_handler):
    """Generator function for video streaming"""
    while True:
        try:
            frame = camera_handler.get_frame_for_streaming()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                time.sleep(0.1)  # Wait if no frame available
        except Exception as e:
            logger.error(f"Error in frame generation: {e}")
            time.sleep(0.1)


@app.route('/api/camera/stream/<int:pond_id>')
def video_feed(pond_id):
    """Video streaming route for MJPEG"""
    try:
        if system is None or system.camera is None:
            return jsonify({"error": "Camera not available"}), 503
        
        return Response(
            generate_frames(system.camera),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Error starting video stream: {e}")
        return jsonify({"error": "Camera not available"}), 503


@app.route('/api/camera/snapshot/<int:pond_id>', methods=['POST'])
def capture_snapshot(pond_id):
    """Capture a snapshot from the camera"""
    try:
        if system is None or system.camera is None:
            return jsonify({"success": False, "message": "Camera not available"}), 503
        
        frame = system.camera.capture_frame()
        if frame is not None:
            filename = f"snapshot_pond{pond_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = system.camera.save_image(frame, filename)
            return jsonify({
                "success": True,
                "message": "Snapshot captured",
                "filename": filename,
                "filepath": filepath
            })
        else:
            return jsonify({"success": False, "message": "Failed to capture frame"}), 500
    except Exception as e:
        logger.error(f"Error capturing snapshot: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/ponds', methods=['GET'])
def get_all_ponds():
    """Get all pond information"""
    try:
        if system is None:
            return jsonify({"success": False, "message": "System not initialized"}), 503
        
        # For now, return a single pond (can be extended for multiple ponds)
        ponds = [
            {
                "id": 1,
                "name": "Main Pond",
                "status": system.pond_status,
                "lastDetectionTime": system.last_detection_time,
                "lastAlertSummary": system.last_alert_summary,
                "cameraStatus": "online" if system.running else "offline"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": ponds
        })
    except Exception as e:
        logger.error(f"Error getting ponds: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Get system status"""
    try:
        if system is None:
            return jsonify({
                "success": True,
                "data": {
                    "running": False,
                    "cameraStatus": "offline"
                }
            })
        
        return jsonify({
            "success": True,
            "data": {
                "running": system.running,
                "cameraStatus": "online" if system.running else "offline",
                "pondStatus": system.pond_status,
                "lastDetectionTime": system.last_detection_time,
                "lastAlertSummary": system.last_alert_summary
            }
        })
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "message": "API server is running",
        "timestamp": datetime.now().isoformat()
    })


def main():
    """Main entry point"""
    global system
    
    logger.info("=" * 60)
    logger.info("Fish Monitoring System - API Server")
    logger.info("=" * 60)
    
    try:
        # Initialize system
        system = FishMonitoringSystem()
        system.start()
        
        # Start Flask server
        logger.info("Starting Flask API server on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if system:
            system.stop()
        logger.info("API server shutdown complete")


if __name__ == "__main__":
    main()
