"""
Notification System for Taskinity.

This module provides functionality for sending notifications about flow execution
via various channels such as email, Slack, and console output.
"""
import json
import logging
import os
import smtplib
import sys
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class NotificationType(Enum):
    """Types of notifications that can be sent."""
    FLOW_START = "flow_start"
    FLOW_SUCCESS = "flow_success"
    FLOW_FAILURE = "flow_failure"
    TASK_START = "task_start"
    TASK_SUCCESS = "task_success"
    TASK_FAILURE = "task_failure"
    SYSTEM = "system"


class NotificationChannel(ABC):
    """Base class for notification channels."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the notification channel.
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def send(self, subject: str, message: str, notification_type: NotificationType) -> bool:
        """
        Send a notification.
        
        Args:
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        pass


class ConsoleNotificationChannel(NotificationChannel):
    """Notification channel that outputs to the console."""
    
    def send(self, subject: str, message: str, notification_type: NotificationType) -> bool:
        """
        Send a notification to the console.
        
        Args:
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            # Format notification
            notification_str = f"\n{'=' * 80}\n"
            notification_str += f"NOTIFICATION: {notification_type.value.upper()}\n"
            notification_str += f"SUBJECT: {subject}\n"
            notification_str += f"{'-' * 80}\n"
            notification_str += f"{message}\n"
            notification_str += f"{'=' * 80}\n"
            
            # Print notification
            print(notification_str, file=sys.stderr)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending console notification: {str(e)}")
            return False


class EmailNotificationChannel(NotificationChannel):
    """Notification channel that sends emails."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        sender: str,
        recipients: List[str],
        use_tls: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the email notification channel.
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            sender: Sender email address
            recipients: List of recipient email addresses
            use_tls: Whether to use TLS (default: True)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender = sender
        self.recipients = recipients
        self.use_tls = use_tls
    
    def send(self, subject: str, message: str, notification_type: NotificationType) -> bool:
        """
        Send a notification via email.
        
        Args:
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = ", ".join(self.recipients)
            msg["Subject"] = f"[Taskinity] {subject}"
            
            # Add notification type to message
            message_with_type = f"Notification Type: {notification_type.value.upper()}\n\n{message}"
            msg.attach(MIMEText(message_with_type, "plain"))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            # Login and send message
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Sent email notification to {len(self.recipients)} recipients")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending email notification: {str(e)}")
            return False


class SlackNotificationChannel(NotificationChannel):
    """Notification channel that sends messages to Slack."""
    
    def __init__(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Slack notification channel.
        
        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel (optional)
            username: Bot username (optional)
            icon_emoji: Bot icon emoji (optional)
            logger: Logger instance (optional)
        """
        super().__init__(logger)
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests is required for Slack notifications. "
                             "Install with: pip install requests")
        
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username or "Taskinity"
        self.icon_emoji = icon_emoji or ":robot_face:"
    
    def send(self, subject: str, message: str, notification_type: NotificationType) -> bool:
        """
        Send a notification to Slack.
        
        Args:
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            True if the notification was sent successfully, False otherwise
        """
        try:
            # Create payload
            payload = {
                "text": f"*{subject}*\n{message}",
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "mrkdwn": True
            }
            
            if self.channel:
                payload["channel"] = self.channel
            
            # Add notification type as attachment
            color_map = {
                NotificationType.FLOW_START: "#2196F3",    # Blue
                NotificationType.FLOW_SUCCESS: "#4CAF50",  # Green
                NotificationType.FLOW_FAILURE: "#F44336",  # Red
                NotificationType.TASK_START: "#2196F3",    # Blue
                NotificationType.TASK_SUCCESS: "#4CAF50",  # Green
                NotificationType.TASK_FAILURE: "#F44336",  # Red
                NotificationType.SYSTEM: "#9C27B0"         # Purple
            }
            
            payload["attachments"] = [{
                "color": color_map.get(notification_type, "#9E9E9E"),
                "text": f"Notification Type: {notification_type.value.upper()}"
            }]
            
            # Send request
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.logger.error(f"Error sending Slack notification: {response.text}")
                return False
            
            self.logger.info("Sent Slack notification")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {str(e)}")
            return False


class NotificationManager:
    """Manager for sending notifications through multiple channels."""
    
    def __init__(
        self,
        config_path: str = "notification_config.json",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the notification manager.
        
        Args:
            config_path: Path to the notification configuration file
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config_path = config_path
        self.channels: List[NotificationChannel] = []
        self.enabled_types: Set[NotificationType] = set()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load notification configuration from file."""
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            self.logger.warning(f"Notification configuration file not found: {self.config_path}")
            self._create_default_config()
            return
        
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # Load enabled notification types
            enabled_types = config.get("enabled_types", [])
            self.enabled_types = {NotificationType(t) for t in enabled_types if t in [nt.value for nt in NotificationType]}
            
            # Load channels
            channels_config = config.get("channels", {})
            
            # Console channel
            if channels_config.get("console", {}).get("enabled", False):
                self.channels.append(ConsoleNotificationChannel(logger=self.logger))
            
            # Email channel
            email_config = channels_config.get("email", {})
            if email_config.get("enabled", False):
                try:
                    self.channels.append(EmailNotificationChannel(
                        smtp_server=email_config["smtp_server"],
                        smtp_port=email_config["smtp_port"],
                        username=email_config["username"],
                        password=email_config["password"],
                        sender=email_config["sender"],
                        recipients=email_config["recipients"],
                        use_tls=email_config.get("use_tls", True),
                        logger=self.logger
                    ))
                except KeyError as e:
                    self.logger.error(f"Missing required email configuration parameter: {str(e)}")
            
            # Slack channel
            slack_config = channels_config.get("slack", {})
            if slack_config.get("enabled", False):
                try:
                    self.channels.append(SlackNotificationChannel(
                        webhook_url=slack_config["webhook_url"],
                        channel=slack_config.get("channel"),
                        username=slack_config.get("username"),
                        icon_emoji=slack_config.get("icon_emoji"),
                        logger=self.logger
                    ))
                except KeyError as e:
                    self.logger.error(f"Missing required Slack configuration parameter: {str(e)}")
            
            self.logger.info(f"Loaded {len(self.channels)} notification channels")
        
        except Exception as e:
            self.logger.error(f"Error loading notification configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default notification configuration file."""
        config = {
            "enabled": True,
            "enabled_types": [nt.value for nt in NotificationType],
            "channels": {
                "console": {
                    "enabled": True
                },
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "username": "user@example.com",
                    "password": "password",
                    "sender": "taskinity@example.com",
                    "recipients": ["user@example.com"],
                    "use_tls": True
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX",
                    "channel": "#taskinity",
                    "username": "Taskinity",
                    "icon_emoji": ":robot_face:"
                }
            }
        }
        
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Created default notification configuration: {self.config_path}")
            
            # Add console channel by default
            self.channels.append(ConsoleNotificationChannel(logger=self.logger))
            self.enabled_types = set(NotificationType)
        
        except Exception as e:
            self.logger.error(f"Error creating default notification configuration: {str(e)}")
    
    def send(self, subject: str, message: str, notification_type: NotificationType) -> None:
        """
        Send a notification through all enabled channels.
        
        Args:
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification
        """
        if not self.channels:
            self.logger.warning("No notification channels configured")
            return
        
        if notification_type not in self.enabled_types:
            self.logger.debug(f"Notification type {notification_type.value} is disabled")
            return
        
        for channel in self.channels:
            channel.send(subject, message, notification_type)
    
    def notify_flow_start(self, flow_name: str, input_data: Dict[str, Any]) -> None:
        """
        Send a notification about flow start.
        
        Args:
            flow_name: Name of the flow
            input_data: Input data for the flow
        """
        subject = f"Flow Started: {flow_name}"
        message = f"Flow '{flow_name}' has started with input data:\n{json.dumps(input_data, indent=2)}"
        self.send(subject, message, NotificationType.FLOW_START)
    
    def notify_flow_success(self, flow_name: str, result: Any, duration: float) -> None:
        """
        Send a notification about flow success.
        
        Args:
            flow_name: Name of the flow
            result: Result of the flow
            duration: Duration of the flow in seconds
        """
        subject = f"Flow Completed: {flow_name}"
        message = f"Flow '{flow_name}' completed successfully in {duration:.2f} seconds.\n\nResult:\n{json.dumps(result, indent=2)}"
        self.send(subject, message, NotificationType.FLOW_SUCCESS)
    
    def notify_flow_failure(self, flow_name: str, error: Exception, duration: float) -> None:
        """
        Send a notification about flow failure.
        
        Args:
            flow_name: Name of the flow
            error: Error that occurred
            duration: Duration of the flow in seconds
        """
        subject = f"Flow Failed: {flow_name}"
        message = f"Flow '{flow_name}' failed after {duration:.2f} seconds.\n\nError: {type(error).__name__}: {str(error)}"
        self.send(subject, message, NotificationType.FLOW_FAILURE)
    
    def notify_task_start(self, flow_name: str, task_name: str, task_input: Any) -> None:
        """
        Send a notification about task start.
        
        Args:
            flow_name: Name of the flow
            task_name: Name of the task
            task_input: Input data for the task
        """
        subject = f"Task Started: {task_name}"
        message = f"Task '{task_name}' in flow '{flow_name}' has started with input:\n{json.dumps(task_input, indent=2)}"
        self.send(subject, message, NotificationType.TASK_START)
    
    def notify_task_success(self, flow_name: str, task_name: str, task_result: Any, duration: float) -> None:
        """
        Send a notification about task success.
        
        Args:
            flow_name: Name of the flow
            task_name: Name of the task
            task_result: Result of the task
            duration: Duration of the task in seconds
        """
        subject = f"Task Completed: {task_name}"
        message = f"Task '{task_name}' in flow '{flow_name}' completed successfully in {duration:.2f} seconds.\n\nResult:\n{json.dumps(task_result, indent=2)}"
        self.send(subject, message, NotificationType.TASK_SUCCESS)
    
    def notify_task_failure(self, flow_name: str, task_name: str, error: Exception, duration: float) -> None:
        """
        Send a notification about task failure.
        
        Args:
            flow_name: Name of the flow
            task_name: Name of the task
            error: Error that occurred
            duration: Duration of the task in seconds
        """
        subject = f"Task Failed: {task_name}"
        message = f"Task '{task_name}' in flow '{flow_name}' failed after {duration:.2f} seconds.\n\nError: {type(error).__name__}: {str(error)}"
        self.send(subject, message, NotificationType.TASK_FAILURE)
    
    def notify_system(self, subject: str, message: str) -> None:
        """
        Send a system notification.
        
        Args:
            subject: Notification subject
            message: Notification message
        """
        self.send(subject, message, NotificationType.SYSTEM)


# Global notification manager instance
_notification_manager = None


def get_notification_manager(config_path: str = "notification_config.json") -> NotificationManager:
    """
    Get the global notification manager instance.
    
    Args:
        config_path: Path to the notification configuration file
        
    Returns:
        Notification manager instance
    """
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager(config_path=config_path)
    
    return _notification_manager
