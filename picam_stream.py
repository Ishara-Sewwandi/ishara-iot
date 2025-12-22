#!/usr/bin/env python3
"""
Pi Camera streaming server using system Picamera2
Continuously captures frames and serves them via a simple socket/file
"""

import sys
import io
import time
import signal
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = False
    
    def write(self, buf):
        self.frame = buf
        return len(buf)

def main():
    picam2 = Picamera2()
    
    # Configure for video
    video_config = picam2.create_video_configuration(
        main={"size": (960, 540), "format": "RGB888"},
        controls={"FrameRate": 25},
        buffer_count=2
    )
    picam2.configure(video_config)
    
    print("Starting Pi Camera...", file=sys.stderr)
    picam2.start()
    time.sleep(0.5)  # Let camera stabilize
    
    print("Camera ready!", file=sys.stderr)
    
    try:
        while True:
            # Capture frame as numpy array
            frame = picam2.capture_array("main")
            
            # Convert to JPEG
            import cv2
            _, jpeg = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR), 
                                    [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Write to stdout
            sys.stdout.buffer.write(b'--frame\r\n')
            sys.stdout.buffer.write(b'Content-Type: image/jpeg\r\n\r\n')
            sys.stdout.buffer.write(jpeg.tobytes())
            sys.stdout.buffer.write(b'\r\n')
            sys.stdout.buffer.flush()
            
            time.sleep(0.04)  # ~25fps
            
    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        picam2.close()
        print("Camera stopped", file=sys.stderr)

if __name__ == "__main__":
    main()
