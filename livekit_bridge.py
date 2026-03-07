#!/usr/bin/env python3
"""
LiveKit Bridge for Koi Fish Camera Server

This script connects to the EXISTING Flask/Socket.IO camera server
running on the Raspberry Pi (192.168.8.101:5000) and re-publishes
the processed frames (with YOLOv8 fish detection overlays) to LiveKit.

Architecture:
  Pi Camera → Flask/SocketIO (local:5000) → This Bridge → LiveKit (VPS)
                  ↑                                           ↓
           Fish Detection                            Dashboard Viewers
           (YOLOv8)                                  (Any Network)

Usage:
    pip install livekit livekit-api python-socketio[client] opencv-python-headless Pillow
    python3 livekit_bridge.py
"""

import asyncio
import signal
import sys
import os
import time
import argparse
import logging
import base64
import io
import threading
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("livekit-bridge")

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
LIVEKIT_URL = os.getenv(
    "LIVEKIT_URL",
    "wss://livekit.koifishfriend.online"
)
API_KEY = os.getenv("LIVEKIT_API_KEY", "APIhfro22ogg9c3")
API_SECRET = os.getenv(
    "LIVEKIT_API_SECRET",
    "5ejwe0usuxnlknv5afgtsyfvsgmukb1pedprwwqaxilc"
)
ROOM_NAME = os.getenv("LIVEKIT_ROOM", "boat-navigation")
PARTICIPANT_IDENTITY = os.getenv("LIVEKIT_IDENTITY", "boat-camera-pi")
PARTICIPANT_NAME = os.getenv("LIVEKIT_NAME", "Boat Camera (RPi + YOLOv8)")

PI_CAMERA_URL = os.getenv("PI_CAMERA_URL", "http://192.168.8.101:5000")

# Shared state
latest_frame_bytes = None
latest_frame_lock = threading.Lock()
frame_width = 640
frame_height = 360
shutdown_event = asyncio.Event()
sio_connected = False


def signal_handler(sig, frame):
    logger.info("Shutdown signal received")
    shutdown_event.set()


# ─────────────────────────────────────────
# Socket.IO Client (receives frames from Pi)
# ─────────────────────────────────────────
def start_socketio_receiver(pi_url):
    """Connect to Pi's Flask/Socket.IO and receive processed frames."""
    global latest_frame_bytes, frame_width, frame_height, sio_connected

    import socketio

    sio = socketio.Client(
        reconnection=True,
        reconnection_delay=2,
        reconnection_attempts=0,  # infinite
        logger=False
    )

    @sio.event
    def connect():
        global sio_connected
        sio_connected = True
        logger.info(f"✅ Connected to Pi camera server: {pi_url}")
        sio.emit('start_stream')

    @sio.event
    def disconnect():
        global sio_connected
        sio_connected = False
        logger.warning("❌ Disconnected from Pi camera server")

    @sio.on('detection_update')
    def on_detection_update(data):
        """Receive processed frame from Pi (with fish detection overlays)."""
        global latest_frame_bytes, frame_width, frame_height

        try:
            if 'frame' in data and data['frame']:
                # Decode base64 JPEG from Pi
                frame_b64 = data['frame']
                frame_jpeg = base64.b64decode(frame_b64)

                # Decode JPEG to get dimensions and RGBA bytes for LiveKit
                from PIL import Image
                img = Image.open(io.BytesIO(frame_jpeg))
                
                # Convert to RGBA (LiveKit needs RGBA)
                img_rgba = img.convert('RGBA')
                
                with latest_frame_lock:
                    frame_width = img_rgba.width
                    frame_height = img_rgba.height
                    latest_frame_bytes = img_rgba.tobytes()

                fps = data.get('fps', 0)
                fish_count = data.get('fish_count', 0)
                
                # Log periodically
                if int(time.time()) % 10 == 0:
                    logger.debug(f"📷 Frame: {frame_width}x{frame_height}, FPS: {fps}, Fish: {fish_count}")

        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    # Connect loop
    while not shutdown_event.is_set():
        try:
            logger.info(f"🔌 Connecting to Pi camera: {pi_url}")
            sio.connect(pi_url, transports=['websocket', 'polling'])
            sio.wait()
        except Exception as e:
            logger.error(f"Socket.IO error: {e}")
            if not shutdown_event.is_set():
                logger.info("Retrying in 5 seconds...")
                time.sleep(5)
        finally:
            try:
                sio.disconnect()
            except:
                pass


# ─────────────────────────────────────────
# LiveKit Publisher (sends frames to VPS)
# ─────────────────────────────────────────
async def publish_to_livekit():
    """Publish received frames to LiveKit room on VPS."""
    global latest_frame_bytes, frame_width, frame_height

    from livekit import rtc
    from livekit.api import AccessToken, VideoGrants

    # Generate access token
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

    # Connect to LiveKit room
    room = rtc.Room()
    logger.info(f"🔌 Connecting to LiveKit: {LIVEKIT_URL}")

    try:
        await room.connect(LIVEKIT_URL, jwt_token)
    except Exception as e:
        logger.error(f"❌ Failed to connect to LiveKit: {e}")
        logger.error("Check:")
        logger.error(f"  1. LiveKit server running at {LIVEKIT_URL}")
        logger.error("  2. SSL certs valid")
        logger.error("  3. API key/secret match")
        return

    logger.info(f"✅ Connected to LiveKit room: {ROOM_NAME}")

    # Wait for first frame to know dimensions
    logger.info("⏳ Waiting for first frame from Pi camera server...")
    while latest_frame_bytes is None and not shutdown_event.is_set():
        await asyncio.sleep(0.1)

    if shutdown_event.is_set():
        await room.disconnect()
        return

    # Create video source with frame dimensions
    with latest_frame_lock:
        w, h = frame_width, frame_height
    
    logger.info(f"📐 Frame dimensions: {w}x{h}")
    source = rtc.VideoSource(w, h)
    track = rtc.LocalVideoTrack.create_video_track("boat-cam", source)

    options = rtc.TrackPublishOptions()
    options.source = rtc.TrackSource.SOURCE_CAMERA
    publication = await room.local_participant.publish_track(track, options)
    logger.info(f"✅ Video track published (SID: {publication.sid})")

    # Frame publishing loop — forward frames from Pi to LiveKit
    target_fps = 15
    frame_interval = 1.0 / target_fps
    frame_count = 0
    start_time = time.time()
    fps_counter = 0
    fps_timer = time.time()
    last_frame_ref = None

    logger.info(f"🎬 Publishing to LiveKit at up to {target_fps} FPS...")
    logger.info("Press Ctrl+C to stop")
    logger.info("-" * 50)

    while not shutdown_event.is_set():
        with latest_frame_lock:
            current_frame = latest_frame_bytes
            current_w = frame_width
            current_h = frame_height

        if current_frame is not None and current_frame is not last_frame_ref:
            try:
                # Create LiveKit video frame from RGBA bytes
                video_frame = rtc.VideoFrame(
                    current_w,
                    current_h,
                    rtc.VideoBufferType.RGBA,
                    current_frame
                )
                source.capture_frame(video_frame)
                last_frame_ref = current_frame

                frame_count += 1
                fps_counter += 1

                # Log every 10 seconds
                now = time.time()
                if now - fps_timer >= 10.0:
                    actual_fps = fps_counter / (now - fps_timer)
                    elapsed = now - start_time
                    logger.info(
                        f"📡 Frames: {frame_count} | "
                        f"FPS: {actual_fps:.1f} | "
                        f"Uptime: {int(elapsed)}s | "
                        f"Pi: {'🟢' if sio_connected else '🔴'}"
                    )
                    fps_counter = 0
                    fps_timer = now

            except Exception as e:
                logger.error(f"Error publishing frame: {e}")

        await asyncio.sleep(frame_interval)

    # Cleanup
    await room.disconnect()
    total_time = time.time() - start_time
    logger.info(f"✅ Done. Published {frame_count} frames in {total_time:.0f}s")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
async def main(pi_url):
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 55)
    logger.info("🐟 Koi Fish LiveKit Bridge")
    logger.info("=" * 55)
    logger.info(f"Pi Camera URL:  {pi_url}")
    logger.info(f"LiveKit URL:    {LIVEKIT_URL}")
    logger.info(f"Room:           {ROOM_NAME}")
    logger.info(f"Identity:       {PARTICIPANT_IDENTITY}")
    logger.info("=" * 55)
    logger.info("")
    logger.info("This bridge connects your Pi camera server to LiveKit.")
    logger.info("Your YOLOv8 fish detection overlays are preserved!")
    logger.info("")

    # Start Socket.IO receiver in a background thread
    sio_thread = threading.Thread(
        target=start_socketio_receiver,
        args=(pi_url,),
        daemon=True
    )
    sio_thread.start()
    logger.info("📡 Started Pi Socket.IO receiver thread")

    # Wait a moment for first connection
    await asyncio.sleep(2)

    # Start LiveKit publisher with reconnection
    attempt = 0
    while not shutdown_event.is_set():
        attempt += 1
        logger.info(f"LiveKit connection attempt #{attempt}...")

        try:
            await publish_to_livekit()
        except Exception as e:
            logger.error(f"LiveKit error: {e}")

        if not shutdown_event.is_set():
            wait_time = min(5 * attempt, 30)
            logger.info(f"Reconnecting to LiveKit in {wait_time}s...")
            await asyncio.sleep(wait_time)
            if attempt > 5:
                attempt = 0

    logger.info("👋 LiveKit bridge stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bridge Pi camera server (Socket.IO) to LiveKit (VPS)"
    )
    parser.add_argument(
        "--pi-url",
        type=str,
        default=PI_CAMERA_URL,
        help=f"Pi camera server URL (default: {PI_CAMERA_URL})"
    )
    args = parser.parse_args()

    asyncio.run(main(args.pi_url))
