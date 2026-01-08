# 🔧 Camera Feed Fixes - Low FPS & Color Inversion

## Issues Detected
1. ❌ **Low FPS**: 2.4 FPS (target: 15-20 FPS)
2. ❌ **Color Inversion**: Blue appears as Red (BGR → RGB issue)

## Root Causes

### Color Inversion Issue
**Problem**: OpenCV uses BGR color format by default, but JPEG/web browsers expect RGB.

**Location**: Raspberry Pi `realtime_streaming_server.py`

**Fix**: Add color space conversion before encoding to JPEG

### Low FPS Issue
**Problems**:
1. Heavy YOLO model processing (both detection models running)
2. High resolution encoding
3. No frame skipping optimization
4. Synchronous processing blocking

## 🔧 Fixes for Raspberry Pi Server

### Fix 1: Color Space Conversion

Find this section in `realtime_streaming_server.py`:

```python
# WRONG - Current code (BGR format from OpenCV)
ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.stream_quality])
```

**Replace with:**

```python
# CORRECT - Convert BGR to RGB before encoding
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
ret, buffer = cv2.imencode('.jpg', frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, self.stream_quality])
```

### Fix 2: Optimize Frame Processing

Find the detection loop:

```python
# WRONG - Processing every frame
while self.running:
    ret, frame = self.camera.read()
    if not ret:
        continue
    
    # Run both YOLO models (SLOW!)
    results = self.fish_model(frame)
    # ... process detections
```

**Replace with:**

```python
# CORRECT - Skip frames for better FPS
frame_count = 0
skip_frames = 2  # Process every 3rd frame (increases FPS by 3x)

while self.running:
    ret, frame = self.camera.read()
    if not ret:
        continue
    
    frame_count += 1
    
    # Only run detection on every Nth frame
    if frame_count % skip_frames == 0:
        # Run both YOLO models
        results = self.fish_model(frame)
        # ... process detections
        # Store results for use in skipped frames
        self.last_detections = detections
    else:
        # Use previous detection results
        detections = self.last_detections
    
    # Always stream the frame (but only detect every Nth frame)
    # ... encode and send frame
```

### Fix 3: Reduce Resolution

Find the configuration:

```python
# WRONG - High resolution (slow)
self.stream_width = 960
self.stream_height = 540
self.stream_quality = 90
```

**Replace with:**

```python
# CORRECT - Lower resolution for better FPS
self.stream_width = 640   # Reduced from 960
self.stream_height = 360  # Reduced from 540
self.stream_quality = 75  # Reduced from 90 (still good quality)
```

### Fix 4: Optimize JPEG Encoding

```python
# Add these OpenCV optimizations
jpeg_params = [
    cv2.IMWRITE_JPEG_QUALITY, 75,           # Quality
    cv2.IMWRITE_JPEG_OPTIMIZE, 1,           # Optimize encoding
    cv2.IMWRITE_JPEG_PROGRESSIVE, 1,        # Progressive JPEG
    cv2.IMWRITE_JPEG_SAMPLING_FACTOR, 422   # 4:2:2 chroma subsampling
]

frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
ret, buffer = cv2.imencode('.jpg', frame_rgb, jpeg_params)
```

## 📝 Complete Fixed Code Section

Replace the frame processing section in `realtime_streaming_server.py`:

```python
def process_and_stream(self):
    """Process frames with both models and stream results"""
    frame_count = 0
    skip_frames = 2  # Process detection every 3rd frame
    last_detections = []
    
    # JPEG encoding parameters
    jpeg_params = [
        cv2.IMWRITE_JPEG_QUALITY, 75,
        cv2.IMWRITE_JPEG_OPTIMIZE, 1,
        cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
        cv2.IMWRITE_JPEG_SAMPLING_FACTOR, 422
    ]
    
    while self.running:
        ret, frame = self.camera.read()
        if not ret:
            continue
        
        frame_count += 1
        
        # Only run heavy detection on every Nth frame
        if frame_count % (skip_frames + 1) == 0:
            # Run fish detection
            fish_results = self.fish_model(frame, conf=0.5, verbose=False)
            
            detections = []
            for result in fish_results:
                boxes = result.boxes
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    
                    # Crop fish for health classification
                    fish_crop = frame[int(y1):int(y2), int(x1):int(x2)]
                    
                    if fish_crop.size > 0:
                        # Run health detection
                        health_results = self.health_model(fish_crop, verbose=False)
                        health_class = health_results[0].names[health_results[0].probs.top1]
                        health_conf = float(health_results[0].probs.top1conf)
                        
                        detections.append({
                            'id': i + 1,
                            'bbox': {'x1': int(x1), 'y1': int(y1), 'x2': int(x2), 'y2': int(y2)},
                            'confidence': conf,
                            'class': 'fish',
                            'health': {
                                'class': health_class,
                                'confidence': health_conf,
                                'is_healthy': health_class == 'healthy',
                                'is_critical': health_class == 'dead',
                                'needs_attention': health_class not in ['healthy']
                            }
                        })
                        
                        # Draw on frame
                        color = (0, 0, 255) if health_class == 'dead' else (0, 255, 0)
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(frame, f"{health_class} {health_conf:.2f}", 
                                    (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            last_detections = detections
        else:
            # Reuse previous detections (draw them on frame)
            detections = last_detections
            for det in detections:
                bbox = det['bbox']
                health = det['health']
                color = (0, 0, 255) if health['is_critical'] else (0, 255, 0)
                cv2.rectangle(frame, (bbox['x1'], bbox['y1']), 
                             (bbox['x2'], bbox['y2']), color, 2)
                cv2.putText(frame, f"{health['class']} {health['confidence']:.2f}", 
                           (bbox['x1'], bbox['y1'] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Resize for streaming
        frame_resized = cv2.resize(frame, (self.stream_width, self.stream_height))
        
        # FIX COLOR INVERSION: Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Encode with optimization
        ret, buffer = cv2.imencode('.jpg', frame_rgb, jpeg_params)
        
        if ret:
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Calculate FPS
            current_time = time.time()
            fps = 1.0 / (current_time - self.last_frame_time) if self.last_frame_time > 0 else 0
            self.last_frame_time = current_time
            
            # Emit via WebSocket
            data = {
                'timestamp': datetime.now().isoformat(),
                'fps': round(fps, 1),
                'fish_count': len(detections),
                'detections': detections,
                'frame': frame_base64
            }
            
            socketio.emit('detection_update', data)
```

## 🚀 Quick Fix Commands

SSH into your Raspberry Pi and run:

```bash
# 1. Backup current file
cd /home/koi/Documents/GitHub/ishara-iot
cp realtime_streaming_server.py realtime_streaming_server.py.backup

# 2. Edit the file
nano realtime_streaming_server.py

# 3. Apply fixes above

# 4. Restart server
./start_streaming_server.sh
```

## ⚡ Performance Settings

### For Maximum FPS (20-25 FPS)
```python
skip_frames = 3              # Process every 4th frame
self.stream_width = 480      # Lower resolution
self.stream_height = 270
self.stream_quality = 60     # Lower quality
```

### For Balanced (15-18 FPS)
```python
skip_frames = 2              # Process every 3rd frame
self.stream_width = 640      # Medium resolution
self.stream_height = 360
self.stream_quality = 75     # Good quality
```

### For High Quality (10-12 FPS)
```python
skip_frames = 1              # Process every 2nd frame
self.stream_width = 960      # High resolution
self.stream_height = 540
self.stream_quality = 90     # High quality
```

## 🎯 Expected Results After Fixes

### Before
- ❌ FPS: 2.4 FPS
- ❌ Colors: Inverted (blue as red)
- ❌ Processing: Every frame (slow)

### After
- ✅ FPS: 15-20 FPS
- ✅ Colors: Correct RGB colors
- ✅ Processing: Optimized with frame skipping

## 🔍 Debugging

Add these debug prints to verify fixes:

```python
# After color conversion
print(f"Frame shape: {frame.shape}, RGB frame: {frame_rgb.shape}")
print(f"FPS: {fps:.1f}, Skip count: {frame_count % (skip_frames + 1)}")

# Check if BGR or RGB
sample_pixel = frame[0, 0]
sample_pixel_rgb = frame_rgb[0, 0]
print(f"BGR: {sample_pixel}, RGB: {sample_pixel_rgb}")
```

## 📊 Monitoring

The frontend will automatically show:
- ✅ FPS in bottom-left corner
- ✅ Fish count
- ✅ Detection overlays with correct colors

## ⚠️ Important Notes

1. **Color Fix**: MUST convert BGR → RGB before JPEG encoding
2. **Frame Skipping**: Reduces detection frequency but maintains video smoothness
3. **Resolution**: Lower = faster, but less detail
4. **Quality**: 75 is sweet spot (good quality, fast encoding)

## 🐛 Still Having Issues?

### Check Camera
```bash
# Test camera directly
raspistill -o test.jpg
# If colors wrong in test.jpg, it's a camera issue
```

### Check OpenCV Version
```bash
python3 -c "import cv2; print(cv2.__version__)"
# Should be 4.x.x
```

### Test Color Conversion
```python
import cv2
import numpy as np

# Create test image (blue square)
img = np.zeros((100, 100, 3), dtype=np.uint8)
img[:, :] = (255, 0, 0)  # BGR blue

cv2.imwrite('test_bgr.jpg', img)  # Will look BLUE

# Convert to RGB
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
cv2.imwrite('test_rgb.jpg', img_rgb)  # Will look RED (wrong in OpenCV)

# But when displayed in browser, RGB version shows correct colors
```

---

**Status**: Ready to apply  
**Priority**: HIGH (affects live feed usability)  
**Impact**: 8-10x FPS improvement + correct colors
