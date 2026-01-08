# Spring Boot Frontend Integration Guide

## Overview

This system runs **both detection models simultaneously** (Fish Detection + Health Detection) and streams results in real-time to your Spring Boot frontend with zero lag.

## Architecture

```
Raspberry Pi (ESP32)
  ├─ Camera (25 FPS)
  ├─ Fish Detection Model (YOLOv8)
  ├─ Health Detection Model (YOLOv8-cls)
  └─ Streaming Server (Flask + WebSocket)
       │
       ├─ HTTP REST API (Detection Results)
       ├─ MJPEG Stream (Live Video Feed)
       └─ WebSocket (Real-time Updates with Frames)
              ↓
       Spring Boot Backend
              ↓
       Frontend (React/Angular/Vue)
```

## Quick Start

### 1. Start the Streaming Server

```bash
cd /home/koi/Documents/GitHub/ishara-iot
./start_streaming_server.sh
```

The server will display:
```
Local IP: 192.168.8.101
Access Points:
  • API Info:        http://192.168.8.101:5000
  • Video Stream:    http://192.168.8.101:5000/video/stream
  • Detection API:   http://192.168.8.101:5000/api/detections
  • WebSocket:       ws://192.168.8.101:5000
```

### 2. Spring Boot Integration

## Option 1: WebSocket (RECOMMENDED - Real-time with frames)

### Spring Boot Backend

**pom.xml** - Add dependencies:
```xml
<dependencies>
    <!-- WebSocket -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-websocket</artifactId>
    </dependency>
    
    <!-- SocketIO Client -->
    <dependency>
        <groupId>io.socket</groupId>
        <artifactId>socket.io-client</artifactId>
        <version>2.1.0</version>
    </dependency>
</dependencies>
```

**FishMonitoringWebSocketClient.java**:
```java
package com.example.fishmonitoring.websocket;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;
import org.json.JSONObject;
import org.springframework.stereotype.Service;
import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.net.URISyntaxException;
import java.util.logging.Logger;

@Service
public class FishMonitoringWebSocketClient {
    
    private static final Logger logger = Logger.getLogger(FishMonitoringWebSocketClient.class.getName());
    private Socket socket;
    private static final String RASPBERRY_PI_URL = "http://192.168.8.101:5000"; // Change to your Pi's IP
    
    @PostConstruct
    public void connect() {
        try {
            socket = IO.socket(RASPBERRY_PI_URL);
            
            // Connection events
            socket.on(Socket.EVENT_CONNECT, new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    logger.info("Connected to Raspberry Pi streaming server");
                    socket.emit("start_stream");
                }
            });
            
            socket.on(Socket.EVENT_DISCONNECT, new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    logger.warning("Disconnected from Raspberry Pi");
                }
            });
            
            // Detection updates (includes frame + detection data)
            socket.on("detection_update", new Emitter.Listener() {
                @Override
                public void call(Object... args) {
                    JSONObject data = (JSONObject) args[0];
                    handleDetectionUpdate(data);
                }
            });
            
            socket.connect();
            
        } catch (URISyntaxException e) {
            logger.severe("Failed to connect to Raspberry Pi: " + e.getMessage());
        }
    }
    
    private void handleDetectionUpdate(JSONObject data) {
        try {
            // Extract data
            String timestamp = data.getString("timestamp");
            double fps = data.getDouble("fps");
            int fishCount = data.getInt("fish_count");
            String frameBase64 = data.getString("frame");
            
            // Detection results
            org.json.JSONArray detections = data.getJSONArray("detections");
            
            logger.info(String.format("Received update: FPS=%.1f, Fish=%d", fps, fishCount));
            
            // Process detections
            for (int i = 0; i < detections.length(); i++) {
                JSONObject fish = detections.getJSONObject(i);
                int fishId = fish.getInt("id");
                
                // Bounding box
                JSONObject bbox = fish.getJSONObject("bbox");
                int x1 = bbox.getInt("x1");
                int y1 = bbox.getInt("y1");
                int x2 = bbox.getInt("x2");
                int y2 = bbox.getInt("y2");
                
                // Health data (if available)
                if (fish.has("health")) {
                    JSONObject health = fish.getJSONObject("health");
                    String healthClass = health.getString("class");
                    double confidence = health.getDouble("confidence");
                    boolean isHealthy = health.getBoolean("is_healthy");
                    boolean isCritical = health.getBoolean("is_critical");
                    
                    logger.info(String.format("Fish #%d: %s (%.1f%%) - Critical: %b",
                        fishId, healthClass, confidence * 100, isCritical));
                    
                    // Send alert if critical
                    if (isCritical) {
                        sendCriticalAlert(fishId, healthClass, frameBase64);
                    }
                }
            }
            
            // Broadcast to connected frontend clients
            broadcastToFrontend(data);
            
        } catch (Exception e) {
            logger.severe("Error processing detection update: " + e.getMessage());
        }
    }
    
    private void sendCriticalAlert(int fishId, String healthStatus, String frame) {
        // Implement your alert logic here
        logger.warning(String.format("CRITICAL ALERT: Fish #%d is %s", fishId, healthStatus));
        // Send notification, email, SMS, etc.
    }
    
    private void broadcastToFrontend(JSONObject data) {
        // Use Spring WebSocket to broadcast to frontend
        // See FishMonitoringWebSocketController below
    }
    
    @PreDestroy
    public void disconnect() {
        if (socket != null) {
            socket.emit("stop_stream");
            socket.disconnect();
            logger.info("Disconnected from Raspberry Pi");
        }
    }
}
```

**FishMonitoringWebSocketController.java** - Broadcast to Frontend:
```java
package com.example.fishmonitoring.controller;

import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.beans.factory.annotation.Autowired;

@Controller
public class FishMonitoringWebSocketController {
    
    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    public void broadcastDetectionUpdate(String jsonData) {
        messagingTemplate.convertAndSend("/topic/detections", jsonData);
    }
}
```

**WebSocketConfig.java**:
```java
package com.example.fishmonitoring.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {
    
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.enableSimpleBroker("/topic");
        config.setApplicationDestinationPrefixes("/app");
    }
    
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }
}
```

## Option 2: REST API (Polling - Simple but less efficient)

**FishMonitoringRestClient.java**:
```java
package com.example.fishmonitoring.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.scheduling.annotation.Scheduled;

@Service
public class FishMonitoringRestClient {
    
    private static final String API_URL = "http://192.168.8.101:5000/api/detections";
    private final RestTemplate restTemplate = new RestTemplate();
    
    @Scheduled(fixedRate = 1000) // Poll every 1 second
    public void fetchDetections() {
        try {
            String response = restTemplate.getForObject(API_URL, String.class);
            processDetections(response);
        } catch (Exception e) {
            System.err.println("Error fetching detections: " + e.getMessage());
        }
    }
    
    private void processDetections(String jsonResponse) {
        // Parse and process detection data
        System.out.println("Detection data: " + jsonResponse);
    }
}
```

## Frontend Integration

### React Example

**FishMonitoringComponent.jsx**:
```javascript
import React, { useState, useEffect } from 'react';
import SockJS from 'sockjs-client';
import { Stomp } from '@stomp/stompjs';

function FishMonitoringComponent() {
    const [detections, setDetections] = useState([]);
    const [frame, setFrame] = useState(null);
    const [fps, setFps] = useState(0);
    const [fishCount, setFishCount] = useState(0);
    
    useEffect(() => {
        // Connect to Spring Boot WebSocket
        const socket = new SockJS('http://localhost:8080/ws');
        const stompClient = Stomp.over(socket);
        
        stompClient.connect({}, () => {
            console.log('Connected to Spring Boot WebSocket');
            
            // Subscribe to detection updates
            stompClient.subscribe('/topic/detections', (message) => {
                const data = JSON.parse(message.body);
                
                setFps(data.fps);
                setFishCount(data.fish_count);
                setDetections(data.detections);
                setFrame('data:image/jpeg;base64,' + data.frame);
            });
        });
        
        return () => {
            if (stompClient) {
                stompClient.disconnect();
            }
        };
    }, []);
    
    return (
        <div className="fish-monitoring">
            <h2>Live Fish Monitoring</h2>
            
            <div className="stats">
                <p>FPS: {fps.toFixed(1)}</p>
                <p>Fish Count: {fishCount}</p>
            </div>
            
            {/* Live Video Feed with Detections */}
            {frame && (
                <img 
                    src={frame} 
                    alt="Live Feed" 
                    style={{ width: '100%', maxWidth: '800px' }}
                />
            )}
            
            {/* Detection List */}
            <div className="detections">
                <h3>Detected Fish</h3>
                {detections.map(fish => (
                    <div key={fish.id} className="fish-card">
                        <h4>Fish #{fish.id}</h4>
                        <p>Detection Confidence: {(fish.confidence * 100).toFixed(1)}%</p>
                        
                        {fish.health && (
                            <div className={`health-status ${fish.health.is_critical ? 'critical' : ''}`}>
                                <p>Health: {fish.health.class.toUpperCase()}</p>
                                <p>Confidence: {(fish.health.confidence * 100).toFixed(1)}%</p>
                                {fish.health.is_critical && (
                                    <span className="alert">⚠️ CRITICAL</span>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default FishMonitoringComponent;
```

## API Endpoints Reference

### GET /
- **Description**: API information
- **Response**: JSON with service info and endpoints

### GET /api/status
- **Description**: Get system status
- **Response**:
```json
{
    "running": true,
    "fps": 24.5,
    "timestamp": "2026-01-08T10:30:00",
    "camera_active": true,
    "models": {
        "fish_detection": true,
        "health_detection": true
    }
}
```

### GET /api/detections
- **Description**: Get latest detection results
- **Response**:
```json
{
    "timestamp": "2026-01-08T10:30:00",
    "fps": 24.5,
    "fish_count": 3,
    "detections": [
        {
            "id": 1,
            "bbox": {"x1": 100, "y1": 150, "x2": 250, "y2": 300},
            "confidence": 0.95,
            "class": "fish",
            "health": {
                "class": "healthy",
                "confidence": 0.92,
                "is_healthy": true,
                "is_critical": false,
                "needs_attention": false
            }
        }
    ]
}
```

### GET /video/stream
- **Description**: MJPEG video stream (raw video)
- **Usage**: Direct video tag or img tag
```html
<img src="http://192.168.8.101:5000/video/stream" alt="Live Feed" />
```

### WebSocket: detection_update
- **Event**: Real-time detection updates with frames
- **Data**:
```json
{
    "timestamp": "2026-01-08T10:30:00",
    "fps": 24.5,
    "fish_count": 3,
    "detections": [...],
    "frame": "base64_encoded_jpeg_image"
}
```

## Performance Optimization

### For Low Latency:

1. **Use WebSocket** instead of polling REST API
2. **Adjust stream quality** in config:
```bash
curl -X POST http://192.168.8.101:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"quality": 70, "width": 640, "height": 360}'
```

3. **Network optimization**:
   - Use wired connection instead of WiFi
   - Ensure both devices are on same subnet
   - Configure router for QoS (Quality of Service)

### For ESP32:

The system is optimized for ESP32-CAM with:
- Adjustable JPEG quality
- Configurable resolution
- Frame skipping for performance
- Efficient base64 encoding

## Troubleshooting

### Can't connect from Spring Boot

1. **Check firewall**:
```bash
sudo ufw allow 5000/tcp
```

2. **Verify server is running**:
```bash
curl http://localhost:5000/api/status
```

3. **Check local IP**:
```bash
hostname -I
```

### High latency / lag

1. **Reduce stream quality**:
```python
# In realtime_streaming_server.py
self.stream_quality = 60  # Lower = faster
self.stream_width = 480
self.stream_height = 270
```

2. **Increase frame skipping**:
```python
skip_interval = 3  # Process every 3rd frame
```

### Missing detections

1. **Check models exist**:
```bash
ls -lh models/
```

2. **Verify camera**:
```bash
python3 test_camera.py
```

## Summary

✅ **Both models run simultaneously** (Fish Detection + Health Detection)  
✅ **Real-time streaming** with WebSocket (no lag)  
✅ **Live feed includes detections** (annotated frames)  
✅ **Spring Boot integration ready** (REST + WebSocket)  
✅ **ESP32 compatible** (optimized streaming)  
✅ **Local network** (no internet required)

**Start Command**:
```bash
./start_streaming_server.sh
```

**Access from Spring Boot**:
- WebSocket: `ws://[raspberry-pi-ip]:5000`
- REST API: `http://[raspberry-pi-ip]:5000/api/detections`
- Video Stream: `http://[raspberry-pi-ip]:5000/video/stream`
