#!/usr/bin/env python3
"""
MediaMTX Camera Streamer with Real-Time Fish Detection

Captures frames from Pi Camera, runs YOLOv8 fish detection + health
classification, draws annotated overlays, and streams via ffmpeg RTMP
to MediaMTX on VPS. Viewers see HLS stream with live detections.

Architecture:
  Pi Camera → YOLOv8 Detection → Annotated Frames → ffmpeg (RTMP) → MediaMTX (VPS)
                                                                        ↓
                                                                  HLS → Frontend

Usage:
    python3 mediamtx_streamer.py
    python3 mediamtx_streamer.py --direct   # No detection, raw camera
    python3 mediamtx_streamer.py --width 480 --height 270 --fps 10
"""

import os
import sys
import cv2
import time
import signal
import logging
import argparse
import subprocess
import threading
import numpy as np
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("mediamtx-streamer")

# ─────────────────────────────────────────
# Configuration (from env or defaults)
# ─────────────────────────────────────────
RTMP_URL = os.getenv("RTMP_URL", "rtmp://187.77.189.5:1935/live/camera")
STREAM_WIDTH = int(os.getenv("STREAM_WIDTH", "640"))
STREAM_HEIGHT = int(os.getenv("STREAM_HEIGHT", "360"))
STREAM_FPS = int(os.getenv("STREAM_FPS", "15"))
STREAM_BITRATE = os.getenv("STREAM_BITRATE", "800k")

# Shutdown flag
shutdown_event = threading.Event()


def signal_handler(sig, frame):
    logger.info("Shutdown signal received (%s)", signal.Signals(sig).name)
    shutdown_event.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class FishDetectionStreamer:
    """
    All-in-one: Camera capture → YOLOv8 detection → Health classification
    → Annotated frame → ffmpeg RTMP stream to MediaMTX
    """

    def __init__(self, width=640, height=360, fps=15, direct_mode=False):
        self.width = width
        self.height = height
        self.fps = fps
        self.direct_mode = direct_mode
        self.ffmpeg_process = None
        self.camera = None
        self.fish_detector = None
        self.fish_health_detector = None

        # Stats
        self.frame_count = 0
        self.detection_count = 0
        self.current_fps = 0.0
        self.last_detections = []
        self.last_health_results = []

        # Detection skip — run detection every Nth frame to save CPU
        self.skip_interval = 3

    def init_camera(self):
        """Initialize the Pi camera via CameraHandler"""
        from camera_handler import CameraHandler
        from config import Config

        config = Config()
        self.camera = CameraHandler(config)
        self.camera.start()
        logger.info("✅ Camera started")

    def init_detectors(self):
        """Load YOLOv8 fish detection + health classification models"""
        if self.direct_mode:
            logger.info("⚡ Direct mode — skipping model loading")
            return

        from fish_detector import FishDetector
        from fish_health_detector import FishHealthDetector
        from config import Config

        config = Config()
        self.fish_detector = FishDetector(config)
        logger.info("✅ YOLOv8 fish detector loaded")

        self.fish_health_detector = FishHealthDetector(config)
        if self.fish_health_detector.model_available:
            logger.info("✅ Fish health classifier loaded")
        else:
            logger.warning("⚠️ Fish health classifier not available")

    def start_ffmpeg(self):
        """Start ffmpeg subprocess to push frames via RTMP to MediaMTX"""
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", "rgb24",
            "-s", f"{self.width}x{self.height}",
            "-r", str(self.fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-b:v", STREAM_BITRATE,
            "-maxrate", STREAM_BITRATE,
            "-bufsize", f"{int(STREAM_BITRATE.replace('k', '')) * 2}k" if 'k' in STREAM_BITRATE else STREAM_BITRATE,
            "-g", str(self.fps * 2),
            "-pix_fmt", "yuv420p",
            "-f", "flv",
            RTMP_URL
        ]
        logger.info(f"Starting ffmpeg → {RTMP_URL}")
        logger.debug(f"ffmpeg cmd: {' '.join(cmd)}")

        self.ffmpeg_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        logger.info("✅ ffmpeg started (PID: %d)", self.ffmpeg_process.pid)

    def stop_ffmpeg(self):
        """Gracefully stop ffmpeg"""
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
            except Exception:
                pass
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except Exception:
                self.ffmpeg_process.kill()
            logger.info("ffmpeg stopped")

    def detect_and_annotate(self, frame):
        """
        Run YOLOv8 fish detection + health classification on frame.
        Returns annotated frame with bounding boxes and overlays.
        """
        if self.fish_detector is None:
            return frame

        try:
            detections = self.fish_detector.detect(frame)
            self.last_detections = detections
            self.detection_count += len(detections)

            # Run health classification on each detected fish
            health_results = []
            if detections and self.fish_health_detector and self.fish_health_detector.model_available:
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    if x2 > x1 and y2 > y1:
                        crop = frame[y1:y2, x1:x2]
                        if crop.size > 0:
                            health = self.fish_health_detector.classify(crop)
                            if health:
                                health['bbox'] = det['bbox']
                                health_results.append(health)

            self.last_health_results = health_results
            return self._draw_overlay(frame.copy(), detections, health_results)

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return frame

    def _draw_overlay(self, frame, detections, health_results):
        """Draw detection boxes, health labels, FPS, and timestamp on frame"""
        # Top-left info bar
        info = f"FPS: {self.current_fps:.1f} | Fish: {len(detections)}"
        cv2.putText(frame, info, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Bottom-left timestamp
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        # Bounding boxes
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']

            # Find matching health result
            health = None
            for h in health_results:
                if h.get('bbox') == det['bbox']:
                    health = h
                    break

            # Color based on health
            if health:
                if health.get('is_critical', False):
                    color = (0, 0, 255)       # Red — dead
                elif health.get('needs_attention', False):
                    color = (0, 165, 255)     # Orange — unhealthy
                elif health.get('is_healthy', True):
                    color = (0, 255, 0)       # Green — healthy
                else:
                    color = (0, 255, 255)     # Yellow — uncertain
            else:
                color = (255, 255, 0)         # Cyan — no health data

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label
            if health and not health.get('uncertain', False):
                label = f"Fish#{i+1}: {health['class']} ({health['confidence']:.0%})"
            else:
                label = f"Fish#{i+1} ({conf:.0%})"

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
            cv2.putText(frame, label, (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        return frame

    def run(self):
        """Main streaming loop"""
        logger.info("=" * 55)
        logger.info("🐟 Koi Fish MediaMTX Camera Streamer")
        logger.info("=" * 55)
        logger.info(f"RTMP Target:  {RTMP_URL}")
        logger.info(f"Resolution:   {self.width}x{self.height} @ {self.fps}fps")
        logger.info(f"Bitrate:      {STREAM_BITRATE}")
        logger.info(f"Detection:    {'DISABLED (direct)' if self.direct_mode else 'YOLOv8 (every 3rd frame)'}")
        logger.info("=" * 55)

        # Initialize
        self.init_camera()
        self.init_detectors()
        self.start_ffmpeg()

        frame_interval = 1.0 / self.fps
        fps_counter = 0
        fps_timer = time.time()
        skip_counter = 0
        start_time = time.time()

        logger.info("🎬 Streaming started — press Ctrl+C to stop")
        logger.info("-" * 55)

        while not shutdown_event.is_set():
            loop_start = time.time()

            try:
                # Capture frame
                raw_frame = self.camera.capture_frame()
                if raw_frame is None:
                    time.sleep(0.01)
                    continue

                # Resize to stream resolution
                frame = cv2.resize(raw_frame, (self.width, self.height))

                # Detection (every Nth frame) or reuse last overlay
                if not self.direct_mode:
                    skip_counter += 1
                    if skip_counter % self.skip_interval == 0:
                        frame = self.detect_and_annotate(frame)
                    else:
                        # Re-draw last known detections on current frame
                        frame = self._draw_overlay(
                            frame, self.last_detections, self.last_health_results
                        )

                # Write frame to ffmpeg stdin (convert BGR → RGB for ffmpeg)
                if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
                    try:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        self.ffmpeg_process.stdin.write(frame_rgb.tobytes())
                    except BrokenPipeError:
                        logger.warning("ffmpeg pipe broken — restarting...")
                        self.stop_ffmpeg()
                        time.sleep(1)
                        self.start_ffmpeg()
                        continue
                else:
                    logger.warning("ffmpeg not running — restarting...")
                    self.stop_ffmpeg()
                    time.sleep(1)
                    self.start_ffmpeg()
                    continue

                self.frame_count += 1
                fps_counter += 1

                # Log stats every 10 seconds
                now = time.time()
                if now - fps_timer >= 10.0:
                    self.current_fps = fps_counter / (now - fps_timer)
                    elapsed = int(now - start_time)
                    logger.info(
                        f"📊 Frames: {self.frame_count} | "
                        f"FPS: {self.current_fps:.1f} | "
                        f"Fish: {len(self.last_detections)} | "
                        f"Uptime: {elapsed}s"
                    )
                    fps_counter = 0
                    fps_timer = now

                # Frame pacing
                elapsed_frame = time.time() - loop_start
                if elapsed_frame < frame_interval:
                    time.sleep(frame_interval - elapsed_frame)

            except Exception as e:
                logger.error(f"Stream loop error: {e}")
                time.sleep(0.1)

        # Cleanup
        logger.info("Shutting down...")
        self.stop_ffmpeg()
        if self.camera:
            self.camera.stop()
        total = time.time() - start_time
        logger.info(f"✅ Done. Streamed {self.frame_count} frames in {total:.0f}s")


def main():
    parser = argparse.ArgumentParser(
        description="MediaMTX Camera Streamer with Fish Detection"
    )
    parser.add_argument("--width", type=int, default=STREAM_WIDTH,
                        help=f"Stream width (default: {STREAM_WIDTH})")
    parser.add_argument("--height", type=int, default=STREAM_HEIGHT,
                        help=f"Stream height (default: {STREAM_HEIGHT})")
    parser.add_argument("--fps", type=int, default=STREAM_FPS,
                        help=f"Stream FPS (default: {STREAM_FPS})")
    parser.add_argument("--direct", action="store_true",
                        help="Direct camera mode — no fish detection")
    args = parser.parse_args()

    streamer = FishDetectionStreamer(
        width=args.width,
        height=args.height,
        fps=args.fps,
        direct_mode=args.direct
    )
    streamer.run()


if __name__ == "__main__":
    main()
