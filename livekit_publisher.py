#!/usr/bin/env python3
"""
LiveKit Camera Publisher with Fish Detection Integration
Streams camera feed with real-time fish detection overlay to LiveKit server
Works from any network via VPS-hosted LiveKit
"""

import asyncio
import cv2
import signal
import sys
import os
import argparse
import logging
import time
from datetime import datetime
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("livekit-fish-cam")

# Import detection modules
from camera_handler import CameraHandler
from fish_detector import FishDetector
from fish_health_detector import FishHealthDetector
from config import Config

# ─────────────────────────────────────────
# LiveKit Configuration
# ─────────────────────────────────────────
LIVEKIT_URL = os.getenv(
    "LIVEKIT_URL",
    "wss://livekit.koifish-livekit-9ae13d-187-77-189-5.traefik.me"
)
API_KEY = os.getenv("LIVEKIT_API_KEY", "APIhfro22ogg9c3")
API_SECRET = os.getenv(
    "LIVEKIT_API_SECRET",
    "5ejwe0usuxnlknv5afgtsyfvsgmukb1pedprwwqaxilc"
)

ROOM_NAME = os.getenv("LIVEKIT_ROOM", "boat-navigation")
PARTICIPANT_IDENTITY = os.getenv("LIVEKIT_IDENTITY", "fish-detection-pi")
PARTICIPANT_NAME = os.getenv("LIVEKIT_NAME", "Fish Detection Camera")

# Shutdown event
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    logger.info("Received shutdown signal (%s)", signal.Signals(sig).name)
    shutdown_event.set()


class FishDetectionPublisher:
    """Combines fish detection with LiveKit publishing"""
    
    def __init__(self, target_fps: int = 15):
        self.config = Config()
        self.camera = CameraHandler(self.config)
        self.fish_detector = FishDetector(self.config)
        self.fish_health_detector = FishHealthDetector(self.config)
        
        self.target_fps = target_fps
        self.running = False
        
        # Detection state
        self.lock = threading.Lock()
        self.latest_frame = None
        self.latest_detections = []
        self.latest_health_results = []
        self.annotated_frame = None
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
    def start_camera(self):
        """Start camera capture"""
        logger.info("Starting camera...")
        self.camera.start()
        self.running = True
        
    def stop_camera(self):
        """Stop camera capture"""
        logger.info("Stopping camera...")
        self.running = False
        self.camera.stop()
        
    def detect_and_annotate(self, frame):
        """Run detection and create annotated frame"""
        try:
            # Run fish detection
            detections = self.fish_detector.detect(frame)
            
            # Run health detection on detected fish
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
            
            # Update state
            with self.lock:
                self.latest_frame = frame
                self.latest_detections = detections
                self.latest_health_results = health_results
                self.annotated_frame = annotated
                self.detection_count += len(detections)
            
            return annotated
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return frame
    
    def _draw_detections(self, frame, detections, health_results):
        """Draw detection boxes and health status on frame"""
        # Draw FPS and stats
        info_text = f"FPS: {self.current_fps:.1f} | Fish: {len(detections)}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw detection boxes
        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            
            # Find corresponding health result
            health = None
            for h in health_results:
                if h['bbox'] == detection['bbox']:
                    health = h
                    break
            
            # Choose color based on health
            if health:
                if health.get('is_critical', False):
                    color = (0, 0, 255)  # Red for critical
                elif health.get('needs_attention', False):
                    color = (0, 165, 255)  # Orange for attention
                elif health.get('is_healthy', True):
                    color = (0, 255, 0)  # Green for healthy
                else:
                    color = (0, 255, 255)  # Yellow for unknown
            else:
                color = (255, 255, 0)  # Cyan for no health data
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with health status
            if health:
                label = f"Fish #{i+1}: {health['class']} ({health['confidence']:.2f})"
            else:
                label = f"Fish #{i+1} ({confidence:.2f})"
            
            # Background for text
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return frame
    
    def get_frame(self):
        """Get latest annotated frame (thread-safe)"""
        with self.lock:
            if self.annotated_frame is not None:
                return self.annotated_frame.copy()
            return None


async def publish_with_detection(publisher: FishDetectionPublisher, 
                                 width: int, height: int, fps: int):
    """Connect to LiveKit and publish frames with fish detection"""
    
    # Import LiveKit SDK
    from livekit import rtc
    from livekit.api import AccessToken, VideoGrants
    
    # ─── Generate Access Token ───
    logger.info(f"Generating token for room: {ROOM_NAME}")
    token = AccessToken(API_KEY, API_SECRET)
    token.with_identity(PARTICIPANT_IDENTITY)
    token.with_name(PARTICIPANT_NAME)
    token.with_grants(VideoGrants(
        room_join=True,
        room=ROOM_NAME,
        can_publish=True,
        can_subscribe=False,
    ))
    jwt_token = token.to_jwt()
    
    # ─── Connect to LiveKit Room ───
    room = rtc.Room()
    logger.info(f"Connecting to LiveKit: {LIVEKIT_URL}")
    
    try:
        await room.connect(LIVEKIT_URL, jwt_token)
    except Exception as e:
        logger.error(f"❌ Failed to connect: {e}")
        logger.error("Check:")
        logger.error(f"  1. LiveKit server is running at {LIVEKIT_URL}")
        logger.error("  2. API key/secret are correct")
        logger.error("  3. Network connectivity: ping 187.77.189.5")
        return
    
    logger.info(f"✅ Connected to LiveKit room: {ROOM_NAME}")
    
    # ─── Start Camera ───
    publisher.start_camera()
    
    # ─── Create and Publish Video Track ───
    source = rtc.VideoSource(width, height)
    track = rtc.LocalVideoTrack.create_video_track("fish-detection-cam", source)
    
    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    publication = await room.local_participant.publish_track(track, options)
    logger.info(f"✅ Video track published (SID: {publication.sid})")
    
    # ─── Frame Publishing Loop ───
    frame_interval = 1.0 / fps
    frame_count = 0
    detection_count = 0
    start_time = time.time()
    fps_counter = 0
    fps_timer = time.time()
    
    # Skip frames for detection (process every 3rd frame)
    skip_counter = 0
    skip_interval = 3
    
    logger.info(f"🎬 Streaming at target {fps} FPS with fish detection...")
    logger.info("Press Ctrl+C to stop")
    logger.info("-" * 60)
    
    while not shutdown_event.is_set() and publisher.running:
        try:
            # Capture frame
            frame = publisher.camera.capture_frame()
            if frame is None:
                await asyncio.sleep(0.01)
                continue
            
            skip_counter += 1
            
            # Run detection on every Nth frame to maintain FPS
            if skip_counter % skip_interval == 0:
                annotated_frame = publisher.detect_and_annotate(frame)
            else:
                # Use last annotated frame or raw frame
                annotated_frame = publisher.get_frame()
                if annotated_frame is None:
                    annotated_frame = frame
            
            # Resize if needed
            if annotated_frame.shape[1] != width or annotated_frame.shape[0] != height:
                annotated_frame = cv2.resize(annotated_frame, (width, height))
            
            # Convert BGR (OpenCV) → RGBA (LiveKit)
            frame_rgba = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGBA)
            
            # Create and publish LiveKit video frame
            video_frame = rtc.VideoFrame(
                width,
                height,
                rtc.VideoBufferType.RGBA,
                frame_rgba.tobytes()
            )
            source.capture_frame(video_frame)
            
            frame_count += 1
            fps_counter += 1
            
            # Update FPS calculation
            now = time.time()
            if now - fps_timer >= 10.0:
                actual_fps = fps_counter / (now - fps_timer)
                publisher.current_fps = actual_fps
                elapsed = now - start_time
                
                with publisher.lock:
                    total_detections = publisher.detection_count
                
                logger.info(
                    f"📡 Frames: {frame_count} | "
                    f"FPS: {actual_fps:.1f} | "
                    f"Fish Detected: {total_detections} | "
                    f"Uptime: {int(elapsed)}s"
                )
                fps_counter = 0
                fps_timer = now
            
            await asyncio.sleep(frame_interval)
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            await asyncio.sleep(0.1)
    
    # ─── Cleanup ───
    logger.info("Shutting down...")
    publisher.stop_camera()
    await room.disconnect()
    total_time = time.time() - start_time
    logger.info(f"✅ Done. Published {frame_count} frames in {total_time:.0f}s")


async def main(args):
    """Main entry with automatic reconnection"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("🐟 Fish Detection LiveKit Camera Publisher")
    logger.info("=" * 60)
    logger.info(f"LiveKit URL:  {LIVEKIT_URL}")
    logger.info(f"Room:         {ROOM_NAME}")
    logger.info(f"Identity:     {PARTICIPANT_IDENTITY}")
    logger.info(f"Resolution:   {args.width}x{args.height}")
    logger.info(f"Target FPS:   {args.fps}")
    logger.info(f"Detection:    Enabled (every 3rd frame)")
    logger.info("=" * 60)
    
    # Create publisher
    publisher = FishDetectionPublisher(target_fps=args.fps)
    
    attempt = 0
    while not shutdown_event.is_set():
        attempt += 1
        logger.info(f"Connection attempt #{attempt}...")
        
        try:
            await publish_with_detection(publisher, args.width, args.height, args.fps)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        
        if not shutdown_event.is_set():
            wait_time = min(5 * attempt, 30)
            logger.info(f"Reconnecting in {wait_time}s...")
            await asyncio.sleep(wait_time)
            if attempt > 5:
                attempt = 0
    
    logger.info("👋 Fish detection camera publisher stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="LiveKit Camera Publisher with Fish Detection"
    )
    parser.add_argument("--width", type=int, default=640, 
                       help="Frame width (default: 640)")
    parser.add_argument("--height", type=int, default=480, 
                       help="Frame height (default: 480)")
    parser.add_argument("--fps", type=int, default=15, 
                       help="Target FPS (default: 15)")
    args = parser.parse_args()
    
    asyncio.run(main(args))
