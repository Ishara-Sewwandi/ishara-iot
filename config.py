"""
Configuration settings for Fish Mortality Detection System
"""

import os


class Config:
    # Camera Settings - Default 25 FPS Mode
    CAMERA_WIDTH = 960   # Reduced resolution for better performance
    CAMERA_HEIGHT = 540  # 16:9 aspect ratio maintained
    FRAME_RATE = 25  # Default 25 FPS for stable performance
    CAMERA_ROTATION = 0
    CAMERA_BUFFER_COUNT = 4  # Number of buffers
    
    # Performance Settings - Optimized for 25 FPS Fish Mortality Detection
    SKIP_FRAMES = 8  # Process every 8th frame for detection (~3 FPS detection, 25 FPS display)
    USE_THREADING = True  # Separate threads for capture and display
    LIGHTWEIGHT_DISPLAY = True  # Minimal overlays for speed
    FAST_INFERENCE = True  # Use half precision and image size reduction for YOLO
    
    # YOLOv8 Model Settings
    YOLO_MODEL_PATH = "models/fish_detection.pt"  # Your trained YOLOv8 model
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45
    YOLO_IMG_SIZE = 320  # Reduced to 320 for maximum speed (fish are large objects)
    YOLO_HALF = False  # Half precision (FP16) - only works with GPU
    YOLO_MAX_DET = 10  # Maximum detections per image (reduce processing)
    YOLO_AGNOSTIC_NMS = True  # Faster NMS
    
    # Behavior Analysis Settings
    FIN_ACTIVITY_THRESHOLD = 0.3  # Below this = inactive fins
    MOVEMENT_THRESHOLD = 0.2  # Below this = minimal movement
    SKIP_BEHAVIOR_ANALYSIS = True  # Skip optical flow for better FPS (uses simple movement only)
    OPTICAL_FLOW_PARAMS = {
        'pyr_scale': 0.5,
        'levels': 2,  # Reduced from 3 to 2 for speed
        'winsize': 10,  # Reduced from 15 to 10 for speed
        'iterations': 2,  # Reduced from 3 to 2 for speed
        'poly_n': 5,
        'poly_sigma': 1.1,  # Reduced from 1.2
        'flags': 0
    }
    
    # Tracking Settings
    MAX_DISAPPEARED_FRAMES = 30  # Frames before considering fish "lost"
    MIN_DETECTION_FRAMES = 5  # Frames to confirm detection
    
    # Rainfall Detection Settings
    RAINFALL_SENSOR_PIN = 17  # GPIO pin for rainfall sensor (if using)
    RAINFALL_CHECK_INTERVAL = 5  # seconds
    RAINFALL_ALERT_COOLDOWN = 300  # seconds (5 minutes)
    USE_VISUAL_RAINFALL_DETECTION = True  # Use camera-based detection
    
    # Alert Settings
    ALERT_METHOD = "both"  # "mobile", "web", or "both"
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    EMAIL_ENABLED = False
    EMAIL_SMTP_SERVER = "smtp.gmail.com"
    EMAIL_SMTP_PORT = 587
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_TO = os.getenv("EMAIL_TO", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    
    # Storage Settings
    IMAGE_SAVE_DIR = "alerts/images"
    LOG_DIR = "logs"
    MAX_STORED_IMAGES = 1000
    
    # System Settings
    ENABLE_GPU = False  # Set to True if using Coral TPU or similar
    VERBOSE = True
    
    # Display Settings - 25 FPS Default Mode
    DISPLAY_ENABLED = True  # Show live camera feed with annotations
    DISPLAY_WIDTH = 960
    DISPLAY_HEIGHT = 540
    DISPLAY_FPS_TARGET = 25  # Target 25 FPS (default mode)
    SMOOTH_DISPLAY = True    # Prioritize smooth 25 FPS display
    REDUCE_OVERLAY = True    # Minimal overlays for performance
    
    def __init__(self):
        """Ensure directories exist"""
        os.makedirs(self.IMAGE_SAVE_DIR, exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(self.YOLO_MODEL_PATH), exist_ok=True)
