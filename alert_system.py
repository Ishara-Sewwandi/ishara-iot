#!/usr/bin/env python3
"""
Alert System
Sends notifications via Telegram, email, and webhooks
"""

import requests
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

logger = logging.getLogger(__name__)


class AlertSystem:
    def __init__(self, config):
        """Initialize alert system"""
        self.config = config
        self.last_alert_time = {}
        self.min_alert_interval = 60  # Minimum seconds between similar alerts
        
    def send_mortality_alert(self, fish_id, behavior, image_path, timestamp):
        """
        Send mortality alert
        
        Args:
            fish_id (int): Fish identifier
            behavior (dict): Behavior analysis results
            image_path (str): Path to evidence image
            timestamp (datetime): Alert timestamp
        """
        alert_key = f"mortality_{fish_id}"
        
        # Check if we recently sent this alert
        if self._is_recently_alerted(alert_key):
            logger.debug(f"Skipping duplicate alert for fish {fish_id}")
            return
        
        # Prepare message
        message = self._format_mortality_message(fish_id, behavior, timestamp)
        
        # Send via configured methods
        success = False
        
        if self.config.ALERT_METHOD in ['telegram', 'both']:
            success |= self._send_telegram(message, image_path)
        
        if self.config.ALERT_METHOD in ['web', 'both']:
            success |= self._send_webhook(message, image_path, alert_type='mortality')
        
        if self.config.EMAIL_ENABLED:
            success |= self._send_email(
                subject="⚠️ Fish Mortality Alert",
                message=message,
                image_path=image_path
            )
        
        if success:
            self.last_alert_time[alert_key] = datetime.now()
            logger.info(f"Mortality alert sent for fish {fish_id}")
        else:
            logger.error(f"Failed to send mortality alert for fish {fish_id}")
    
    def send_rainfall_alert(self, intensity, image_path, timestamp):
        """
        Send rainfall alert
        
        Args:
            intensity (str): Rainfall intensity
            image_path (str): Path to evidence image
            timestamp (datetime): Alert timestamp
        """
        alert_key = "rainfall"
        
        # Check if we recently sent this alert
        if self._is_recently_alerted(alert_key):
            logger.debug("Skipping duplicate rainfall alert")
            return
        
        # Prepare message
        message = self._format_rainfall_message(intensity, timestamp)
        
        # Send via configured methods
        success = False
        
        if self.config.ALERT_METHOD in ['telegram', 'both']:
            success |= self._send_telegram(message, image_path)
        
        if self.config.ALERT_METHOD in ['web', 'both']:
            success |= self._send_webhook(message, image_path, alert_type='rainfall')
        
        if self.config.EMAIL_ENABLED:
            success |= self._send_email(
                subject="🌧️ Rainfall Alert",
                message=message,
                image_path=image_path
            )
        
        if success:
            self.last_alert_time[alert_key] = datetime.now()
            logger.info("Rainfall alert sent")
        else:
            logger.error("Failed to send rainfall alert")
    
    def _format_mortality_message(self, fish_id, behavior, timestamp):
        """Format mortality alert message"""
        message = f"""
🚨 FISH MORTALITY ALERT 🚨

Fish ID: {fish_id}
Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ Warning Indicators:
• Fin Activity: {behavior['fin_activity']:.2%}
• Side Floating: {'YES' if behavior['is_side_floating'] else 'NO'}
• Movement Score: {behavior['movement_score']:.2%}

Please check the pond immediately!
        """.strip()
        
        return message
    
    def _format_rainfall_message(self, intensity, timestamp):
        """Format rainfall alert message"""
        message = f"""
🌧️ RAINFALL DETECTED 🌧️

Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Intensity: {intensity.upper()}

Prepare for environmental changes:
• Monitor water pH and oxygen levels
• Check water temperature
• Ensure proper drainage
• Be ready for water quality changes
        """.strip()
        
        return message
    
    def _send_telegram(self, message, image_path=None):
        """Send alert via Telegram bot"""
        if not self.config.TELEGRAM_BOT_TOKEN or not self.config.TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}"
            
            # Send text message
            text_url = f"{url}/sendMessage"
            response = requests.post(text_url, data={
                'chat_id': self.config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Telegram message failed: {response.text}")
                return False
            
            # Send image if available
            if image_path and os.path.exists(image_path):
                photo_url = f"{url}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': self.config.TELEGRAM_CHAT_ID}
                    response = requests.post(photo_url, files=files, data=data, timeout=10)
                    
                    if response.status_code != 200:
                        logger.error(f"Telegram photo failed: {response.text}")
            
            logger.info("Telegram alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def _send_webhook(self, message, image_path, alert_type):
        """Send alert via webhook"""
        if not self.config.WEBHOOK_URL:
            logger.warning("Webhook URL not configured")
            return False
        
        try:
            payload = {
                'type': alert_type,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path
            }
            
            response = requests.post(
                self.config.WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Webhook alert sent successfully")
                return True
            else:
                logger.error(f"Webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
            return False
    
    def _send_email(self, subject, message, image_path=None):
        """Send alert via email"""
        if not self.config.EMAIL_ENABLED:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_FROM
            msg['To'] = self.config.EMAIL_TO
            msg['Subject'] = subject
            
            # Add text
            msg.attach(MIMEText(message, 'plain'))
            
            # Add image if available
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', 
                                 filename=os.path.basename(image_path))
                    msg.attach(img)
            
            # Send email
            with smtplib.SMTP(self.config.EMAIL_SMTP_SERVER, self.config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(self.config.EMAIL_FROM, self.config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info("Email alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def _is_recently_alerted(self, alert_key):
        """Check if we recently sent this type of alert"""
        if alert_key not in self.last_alert_time:
            return False
        
        time_since_last = (datetime.now() - self.last_alert_time[alert_key]).total_seconds()
        return time_since_last < self.min_alert_interval
