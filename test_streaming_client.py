#!/usr/bin/env python3
"""
Test client for Real-Time Streaming Server
Tests WebSocket connection and displays received frames
"""

import socketio
import cv2
import numpy as np
import base64
import json
import time
from datetime import datetime

# Create SocketIO client
sio = socketio.Client()

# Statistics
frame_count = 0
start_time = time.time()

@sio.on('connect')
def on_connect():
    print("✅ Connected to streaming server")
    print(f"Connection ID: {sio.sid}")
    sio.emit('start_stream')

@sio.on('disconnect')
def on_disconnect():
    print("❌ Disconnected from server")

@sio.on('connection_response')
def on_connection_response(data):
    print(f"Server response: {data['message']}")

@sio.on('detection_update')
def on_detection_update(data):
    global frame_count, start_time
    
    try:
        # Parse data
        timestamp = data['timestamp']
        fps = data['fps']
        fish_count = data['fish_count']
        detections = data['detections']
        frame_base64 = data['frame']
        
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64)
        frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
        
        # Update statistics
        frame_count += 1
        elapsed = time.time() - start_time
        client_fps = frame_count / elapsed if elapsed > 0 else 0
        
        # Print detection info
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Update received:")
        print(f"  Server FPS: {fps:.1f}")
        print(f"  Client FPS: {client_fps:.1f}")
        print(f"  Fish Count: {fish_count}")
        
        # Print detection details
        for fish in detections:
            print(f"\n  Fish #{fish['id']}:")
            print(f"    Detection confidence: {fish['confidence']*100:.1f}%")
            
            if 'health' in fish:
                health = fish['health']
                status_icon = "🔴" if health['is_critical'] else "🟢" if health['is_healthy'] else "🟠"
                print(f"    Health: {status_icon} {health['class'].upper()} ({health['confidence']*100:.1f}%)")
                
                if health['is_critical']:
                    print(f"    ⚠️  CRITICAL ALERT!")
        
        # Display frame
        if frame is not None:
            cv2.imshow('Real-Time Stream', frame)
            
            # Non-blocking wait
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nQuitting...")
                sio.disconnect()
                cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error processing frame: {e}")

def main():
    # Server URL (change to your Raspberry Pi IP)
    SERVER_URL = 'http://localhost:5000'
    
    print("=" * 60)
    print("Real-Time Streaming Test Client")
    print("=" * 60)
    print(f"Connecting to: {SERVER_URL}")
    print("Press 'q' in the video window to quit")
    print("=" * 60)
    print()
    
    try:
        # Connect to server
        sio.connect(SERVER_URL)
        
        # Wait for events
        sio.wait()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        if sio.connected:
            sio.disconnect()
        cv2.destroyAllWindows()
        
        # Print statistics
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"\n\nStatistics:")
        print(f"  Frames received: {frame_count}")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Average FPS: {avg_fps:.1f}")
        print("\nTest complete!")

if __name__ == "__main__":
    main()
