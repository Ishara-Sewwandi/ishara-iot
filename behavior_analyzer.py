#!/usr/bin/env python3
"""
Behavior Analyzer
Analyzes fish behavior including fin activity, side-floating, and movement patterns
Uses optical flow analysis
"""

import cv2
import numpy as np
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class BehaviorAnalyzer:
    def __init__(self, config):
        """Initialize behavior analyzer"""
        self.config = config
        self.prev_gray = None
        self.fish_tracks = defaultdict(lambda: {
            'history': deque(maxlen=30),
            'optical_flow_history': deque(maxlen=10),
            'orientation_history': deque(maxlen=20)
        })
        self.next_fish_id = 0
        
    def analyze(self, frame, detections, frame_count):
        """
        Analyze fish behavior
        
        Args:
            frame (numpy.ndarray): Current frame
            detections (list): Fish detections
            frame_count (int): Current frame number
            
        Returns:
            dict: Behavior analysis for each fish
                  {fish_id: {'fin_activity': float, 'is_side_floating': bool, 
                             'movement_score': float}}
        """
        results = {}
        
        # Convert to grayscale for optical flow
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Match detections to tracked fish
        matched_fish = self._match_detections(detections)
        
        for fish_id, detection in matched_fish.items():
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            
            # Extract fish region
            fish_region = frame[y1:y2, x1:x2]
            fish_gray = gray[y1:y2, x1:x2]
            
            # Analyze fin activity using optical flow
            fin_activity = self._analyze_fin_activity(fish_gray, fish_id)
            
            # Detect side-floating behavior
            is_side_floating = self._detect_side_floating(fish_region, fish_id)
            
            # Calculate movement score
            movement_score = self._calculate_movement(bbox, fish_id)
            
            # Store results
            results[fish_id] = {
                'fin_activity': fin_activity,
                'is_side_floating': is_side_floating,
                'movement_score': movement_score,
                'bbox': bbox
            }
            
            # Update track history
            self.fish_tracks[fish_id]['history'].append({
                'frame': frame_count,
                'bbox': bbox,
                'behavior': results[fish_id]
            })
        
        # Update previous frame
        self.prev_gray = gray.copy()
        
        return results
    
    def _match_detections(self, detections):
        """
        Match current detections to tracked fish using IoU
        
        Args:
            detections (list): Current frame detections
            
        Returns:
            dict: {fish_id: detection}
        """
        matched = {}
        
        if not self.fish_tracks:
            # First frame - assign new IDs
            for det in detections:
                matched[self.next_fish_id] = det
                self.next_fish_id += 1
            return matched
        
        # Simple matching based on IoU with previous positions
        used_detections = set()
        
        for fish_id, track in self.fish_tracks.items():
            if not track['history']:
                continue
            
            prev_bbox = track['history'][-1]['bbox']
            best_iou = 0
            best_idx = -1
            
            for idx, det in enumerate(detections):
                if idx in used_detections:
                    continue
                
                iou = self._calculate_iou(prev_bbox, det['bbox'])
                if iou > best_iou:
                    best_iou = iou
                    best_idx = idx
            
            if best_iou > 0.3:  # Threshold for matching
                matched[fish_id] = detections[best_idx]
                used_detections.add(best_idx)
        
        # Assign new IDs to unmatched detections
        for idx, det in enumerate(detections):
            if idx not in used_detections:
                matched[self.next_fish_id] = det
                self.next_fish_id += 1
        
        return matched
    
    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def _analyze_fin_activity(self, fish_gray, fish_id):
        """
        Analyze fin movement using optical flow
        
        Returns:
            float: Fin activity score (0-1, higher = more active)
        """
        # Skip optical flow if configured for better performance
        if self.config.SKIP_BEHAVIOR_ANALYSIS:
            return 0.5  # Return neutral score
            
        if self.prev_gray is None or fish_gray.size == 0:
            return 1.0
        
        try:
            # Get previous fish region (approximate)
            track = self.fish_tracks[fish_id]
            if len(track['history']) < 2:
                return 1.0
            
            prev_bbox = track['history'][-2]['bbox']
            x1, y1, x2, y2 = prev_bbox
            
            # Ensure valid region
            h, w = self.prev_gray.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                return 1.0
            
            prev_fish_gray = self.prev_gray[y1:y2, x1:x2]
            
            # Resize to match current size
            if prev_fish_gray.shape != fish_gray.shape:
                prev_fish_gray = cv2.resize(prev_fish_gray, (fish_gray.shape[1], fish_gray.shape[0]))
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_fish_gray,
                fish_gray,
                None,
                **self.config.OPTICAL_FLOW_PARAMS
            )
            
            # Calculate magnitude of flow
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            
            # Focus on edges (where fins typically are)
            edges = cv2.Canny(fish_gray, 50, 150)
            edge_flow = magnitude * (edges > 0)
            
            # Calculate activity score
            activity_score = np.mean(edge_flow) / 10.0  # Normalize
            activity_score = min(1.0, activity_score)
            
            track['optical_flow_history'].append(activity_score)
            
            # Average over history for stability
            return np.mean(track['optical_flow_history'])
            
        except Exception as e:
            logger.debug(f"Error in fin activity analysis: {e}")
            return 1.0
    
    def _detect_side_floating(self, fish_region, fish_id):
        """
        Detect if fish is floating on its side
        
        Returns:
            bool: True if side-floating detected
        """
        if fish_region.size == 0:
            return False
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(fish_region, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return False
            
            # Get largest contour (fish body)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Fit ellipse to determine orientation
            if len(largest_contour) >= 5:
                ellipse = cv2.fitEllipse(largest_contour)
                angle = ellipse[2]
                
                # Check if fish is oriented sideways (not vertical or horizontal swimming)
                # Normal swimming: angle close to 0° or 180° (horizontal)
                # Side floating: angle close to 90° or 270° (vertical)
                
                normalized_angle = angle % 180
                is_sideways = 70 < normalized_angle < 110  # Within 20° of vertical
                
                # Store orientation history
                track = self.fish_tracks[fish_id]
                track['orientation_history'].append(is_sideways)
                
                # Confirm side-floating if consistently sideways
                if len(track['orientation_history']) >= 10:
                    sideways_ratio = sum(track['orientation_history']) / len(track['orientation_history'])
                    return sideways_ratio > 0.7
            
            return False
            
        except Exception as e:
            logger.debug(f"Error in side-floating detection: {e}")
            return False
    
    def _calculate_movement(self, current_bbox, fish_id):
        """
        Calculate movement score based on position changes
        
        Returns:
            float: Movement score (0-1, higher = more movement)
        """
        track = self.fish_tracks[fish_id]
        
        if len(track['history']) < 5:
            return 1.0
        
        # Calculate center points
        centers = []
        for entry in list(track['history'])[-10:]:
            bbox = entry['bbox']
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            centers.append((center_x, center_y))
        
        # Calculate total displacement
        total_distance = 0
        for i in range(1, len(centers)):
            dx = centers[i][0] - centers[i-1][0]
            dy = centers[i][1] - centers[i-1][1]
            distance = np.sqrt(dx**2 + dy**2)
            total_distance += distance
        
        # Normalize movement score
        # Assume average active fish moves ~20 pixels per frame
        movement_score = min(1.0, total_distance / (len(centers) * 20))
        
        return movement_score
