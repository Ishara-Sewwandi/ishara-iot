#!/usr/bin/env python3
"""
Real-Time Streaming Server for Fish Monitoring System
Runs both Fish Detection and Health Detection simultaneously
Streams live feed with detection results to Spring Boot frontend
Optimized for ESP32 and low-latency network streaming
"""

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import logging
import cv2
import numpy as np
import json
import base64

from camera_handler import CameraHandler
from fish_detector import FishDetector
from fish_health_detector import FishHealthDetector
from behavior_analyzer import BehaviorAnalyzer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for local network
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', 
                    ping_timeout=60, ping_interval=25)

# Global variables
system = None
stream_active = False
detection_results = {
    'detections': [],
    'health_results': [],
    'timestamp': None,
    'fps': 0,
    'fish_count': 0
}


class RealtimeStreamingSystem:
    def __init__(self):
        """Initialize the real-time streaming system"""
        logger.info("Initializing Real-Time Streaming System...")
        
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.fish_detector = FishDetector(self.config)
        self.fish_health_detector = FishHealthDetector(self.config)
        self.behavior_analyzer = BehaviorAnalyzer(self.config)
        
        self.running = False
        self.streaming_thread = None
        self.detection_thread = None
        
        # Shared data with locks
        self.lock = threading.Lock()
        self.latest_frame = None
        self.latest_detections = []
        self.latest_health_results = []
        self.annotated_frame = None
        
        # Performance tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Stream settings
        self.stream_quality = 80  # JPEG quality (1-100)
        self.stream_width = 640   # Reduced for network efficiency
        self.stream_height = 360
        
        logger.info("System initialized successfully")
    
    def start(self):
        """Start the streaming system"""
        logger.info("Starting real-time streaming system...")
        self.running = True
        
        # Start camera
        self.camera.start()
        
        # Start detection thread (runs both models)
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        # Start streaming thread
        self.streaming_thread = threading.Thread(target=self._streaming_loop)
        self.streaming_thread.daemon = True
        self.streaming_thread.start()
        
        logger.info("Streaming system started")
    
    def stop(self):
        """Stop the streaming system"""
        logger.info("Stopping streaming system...")
        self.running = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=3)
        
        if self.streaming_thread:
            self.streaming_thread.join(timeout=3)
        
        self.camera.stop()
        logger.info("Streaming system stopped")
    
    def _detection_loop(self):
        """Background detection loop - runs both models simultaneously"""
        frame_skip = 0
        skip_interval = 2  # Process every 2nd frame for speed
        
        while self.running:
            try:
                # Capture frame
                frame = self.camera.capture_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                frame_skip += 1
                
                # Skip frames for performance
                if frame_skip % skip_interval != 0:
                    with self.lock:
                        self.latest_frame = frame.copy()
                    continue
                
                # Run fish detection (Model 1)
                detections = self.fish_detector.detect(frame)
                
                # Run health detection on each detected fish (Model 2)
                health_results = []
                if detections:
                    for detection in detections:
                        bbox = detection['bbox']
                        x1, y1, x2, y2 = bbox
                        
                        # Ensure valid crop
                        if x2 > x1 and y2 > y1:
                            fish_crop = frame[y1:y2, x1:x2]
                            
                            if fish_crop.size > 0:
                                health_result = self.fish_health_detector.classify(fish_crop)
                                if health_result:
                                    health_result['bbox'] = bbox
                                    health_results.append(health_result)
                
                # Create annotated frame
                annotated = self._draw_detections(frame.copy(), detections, health_results)
                
                # Update shared data
                with self.lock:
                    self.latest_frame = frame.copy()
                    self.latest_detections = detections
                    self.latest_health_results = health_results
                    self.annotated_frame = annotated
                
                # Update FPS
                self.frame_count += 1
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.fps_start_time
                    self.current_fps = 30 / elapsed
                    self.fps_start_time = time.time()
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}", exc_info=True)
                time.sleep(0.1)
    
    def _streaming_loop(self):
        """Background streaming loop - sends data via WebSocket"""
        while self.running:
            try:
                with self.lock:
                    if self.annotated_frame is not None:
                        frame = self.annotated_frame.copy()
                        detections = self.latest_detections.copy() if self.latest_detections else []
                        health_results = self.latest_health_results.copy() if self.latest_health_results else []
                    else:
                        time.sleep(0.01)
                        continue
                
                # Resize frame for network efficiency
                frame_resized = cv2.resize(frame, (self.stream_width, self.stream_height))
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame_resized, 
                                          [cv2.IMWRITE_JPEG_QUALITY, self.stream_quality])
                
                if not ret:
                    continue
                
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Prepare detection data
                detection_data = {
                    'timestamp': datetime.now().isoformat(),
                    'fps': round(self.current_fps, 1),
                    'fish_count': len(detections),
                    'detections': self._serialize_detections(detections, health_results),
                    'frame': frame_base64
                }
                
                # Emit via WebSocket
                socketio.emit('detection_update', detection_data, namespace='/')
                
                # Small delay to control stream rate (~15-20 FPS for network)
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}", exc_info=True)
                time.sleep(0.1)
    
    def _draw_detections(self, frame, detections, health_results):
        """Draw detection boxes and health status on frame"""
        if not detections:
            return frame
        
        for i, detection in enumerate(detections):
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            confidence = detection['confidence']
            
            # Find matching health result
            health = None
            for hr in health_results:
                if hr.get('bbox') == bbox:
                    health = hr
                    break
            
            # Determine color based on health
            if health:
                if health.get('is_critical'):
                    color = (0, 0, 255)  # Red - Critical/Dead
                    thickness = 3
                elif not health.get('is_healthy'):
                    color = (0, 165, 255)  # Orange - Disease
                    thickness = 2
                else:
                    color = (0, 255, 0)  # Green - Healthy
                    thickness = 2
            else:
                color = (255, 255, 0)  # Yellow - No health data
                thickness = 2
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Create label
            label = f"Fish #{i+1}"
            if health:
                health_class = health.get('class', 'unknown').upper()
                health_conf = health.get('confidence', 0) * 100
                label += f" - {health_class} ({health_conf:.0f}%)"
            
            # Draw label background
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), color, -1)
            cv2.putText(frame, label, (x1 + 2, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw FPS and info
        info_text = f"FPS: {self.current_fps:.1f} | Fish: {len(detections)}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def _serialize_detections(self, detections, health_results):
        """Convert detection data to JSON-serializable format"""
        result = []
        
        for i, detection in enumerate(detections):
            bbox = detection['bbox']
            
            # Find matching health result
            health = None
            for hr in health_results:
                if hr.get('bbox') == bbox:
                    health = hr
                    break
            
            fish_data = {
                'id': i + 1,
                'bbox': {
                    'x1': int(bbox[0]),
                    'y1': int(bbox[1]),
                    'x2': int(bbox[2]),
                    'y2': int(bbox[3])
                },
                'confidence': float(detection['confidence']),
                'class': detection.get('class', 'fish')
            }
            
            # Add health data if available
            if health:
                fish_data['health'] = {
                    'class': health.get('class', 'unknown'),
                    'confidence': float(health.get('confidence', 0)),
                    'is_healthy': health.get('is_healthy', False),
                    'is_critical': health.get('is_critical', False),
                    'needs_attention': health.get('needs_attention', False)
                }
            
            result.append(fish_data)
        
        return result
    
    def get_jpeg_stream(self):
        """Generate MJPEG stream for HTTP streaming"""
        while self.running:
            try:
                with self.lock:
                    if self.annotated_frame is not None:
                        frame = self.annotated_frame.copy()
                    else:
                        time.sleep(0.01)
                        continue
                
                # Encode as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, 
                                          [cv2.IMWRITE_JPEG_QUALITY, self.stream_quality])
                
                if not ret:
                    continue
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error generating JPEG stream: {e}")
                break


# Flask Routes

@app.route('/')
def index():
    """API information"""
    return jsonify({
        'service': 'Fish Monitoring Real-Time Streaming API',
        'version': '2.0',
        'status': 'active' if system and system.running else 'inactive',
        'endpoints': {
            'GET /api/status': 'Get system status',
            'GET /api/detections': 'Get latest detection results',
            'GET /video/stream': 'MJPEG video stream',
            'WebSocket /': 'Real-time detection updates with frames'
        },
        'features': [
            'Fish Detection (YOLOv8)',
            'Health Detection (6 classes)',
            'Real-time streaming',
            'WebSocket support',
            'Low-latency network streaming'
        ]
    })


@app.route('/api/status')
def get_status():
    """Get system status"""
    if not system:
        return jsonify({'error': 'System not initialized'}), 500
    
    return jsonify({
        'running': system.running,
        'fps': round(system.current_fps, 1),
        'timestamp': datetime.now().isoformat(),
        'camera_active': system.camera.is_running if system.camera else False,
        'models': {
            'fish_detection': True,
            'health_detection': system.fish_health_detector.model_available
        }
    })


@app.route('/api/detections')
def get_detections():
    """Get latest detection results"""
    if not system:
        return jsonify({'error': 'System not initialized'}), 500
    
    with system.lock:
        detections = system.latest_detections.copy() if system.latest_detections else []
        health_results = system.latest_health_results.copy() if system.latest_health_results else []
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'fps': round(system.current_fps, 1),
        'fish_count': len(detections),
        'detections': system._serialize_detections(detections, health_results)
    })


@app.route('/video/stream')
def video_stream():
    """MJPEG video stream endpoint"""
    if not system:
        return "System not initialized", 500
    
    return Response(system.get_jpeg_stream(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/config', methods=['GET', 'POST'])
def config_endpoint():
    """Get or update stream configuration"""
    if not system:
        return jsonify({'error': 'System not initialized'}), 500
    
    if request.method == 'POST':
        data = request.json
        
        if 'quality' in data:
            system.stream_quality = max(1, min(100, int(data['quality'])))
        
        if 'width' in data and 'height' in data:
            system.stream_width = int(data['width'])
            system.stream_height = int(data['height'])
        
        return jsonify({'message': 'Configuration updated'})
    
    return jsonify({
        'quality': system.stream_quality,
        'resolution': {
            'width': system.stream_width,
            'height': system.stream_height
        }
    })


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {
        'status': 'connected',
        'message': 'Connected to Fish Monitoring Streaming Server'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('start_stream')
def handle_start_stream():
    """Start streaming to specific client"""
    logger.info(f"Stream started for client: {request.sid}")
    emit('stream_started', {'status': 'streaming'})


@socketio.on('stop_stream')
def handle_stop_stream():
    """Stop streaming to specific client"""
    logger.info(f"Stream stopped for client: {request.sid}")
    emit('stream_stopped', {'status': 'stopped'})


def main():
    """Main entry point"""
    global system
    
    logger.info("=" * 60)
    logger.info("Real-Time Fish Monitoring Streaming Server")
    logger.info("Features: Fish Detection + Health Detection + Live Streaming")
    logger.info("=" * 60)
    
    # Initialize system
    system = RealtimeStreamingSystem()
    system.start()
    
    try:
        # Get local IP
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("Server Starting...")
        logger.info(f"Local IP: {local_ip}")
        logger.info(f"Access from local network:")
        logger.info(f"  • API: http://{local_ip}:5000")
        logger.info(f"  • Video Stream: http://{local_ip}:5000/video/stream")
        logger.info(f"  • WebSocket: ws://{local_ip}:5000")
        logger.info("")
        logger.info("Spring Boot Frontend Integration:")
        logger.info(f"  • REST API: http://{local_ip}:5000/api/detections")
        logger.info(f"  • WebSocket: ws://{local_ip}:5000")
        logger.info("=" * 60)
        
        # Run Flask-SocketIO server
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, 
                    allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if system:
            system.stop()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()
