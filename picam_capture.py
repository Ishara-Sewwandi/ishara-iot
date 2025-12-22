#!/usr/bin/env python3
"""
Simple Pi Camera capture script using system Picamera2
This runs with system Python which has libcamera access
"""

import sys
import io
from picamera2 import Picamera2
import time

def capture_frame():
    """Capture a single frame and write to stdout as JPEG"""
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (960, 540)},
        buffer_count=1
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(0.1)  # Let camera warm up
    
    # Capture to memory
    stream = io.BytesIO()
    picam2.capture_file(stream, format='jpeg')
    
    # Write to stdout
    sys.stdout.buffer.write(stream.getvalue())
    
    picam2.stop()
    picam2.close()

if __name__ == "__main__":
    try:
        capture_frame()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
