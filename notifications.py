"""
Notifications System - LaserFlow
Manages application notifications and alerts
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QIcon, QAction
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import List, Optional


class Notification(QObject):
    """Single notification"""
    
    def __init__(self, title: str, message: str, notification_type: str = "info", duration: int = 5000):
        super().__init__()
        self.title = title
        self.message = message
        self.type = notification_type  # info, warning, error, success
        self.duration = duration
        self.created_at = datetime.now()
        self.read = False


class NotificationManager(QObject):
    """Manages application notifications"""
    
    notification_added = Signal(object)  # Emits Notification object
    notification_removed = Signal(str)  # Emits notification ID
    
    def __init__(self):
        super().__init__()
        self.notifications: List[Notification] = []
        self.max_notifications = 50
        self.db_path = Path("notifications.db")
        self.tray_icon = None
        self._setup_tray_icon()
        self._load_notifications()
    
    def _setup_tray_icon(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon()
        
        # Set icon
        icon_path = Path("app_icon.ico")
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # Use default icon
            self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon))
        
        # Create menu
        menu = QMenu()
        
        show_action = QAction("Show Notifications", menu)
        show_action.triggered.connect(self._show_notifications)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        clear_action = QAction("Clear All", menu)
        clear_action.triggered.connect(self._clear_all)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_notifications()
    
    def _show_notifications(self):
        """Show notifications window"""
        # This will be implemented in the UI
        pass
    
    def _clear_all(self):
        """Clear all notifications"""
        self.notifications.clear()
        self._save_notifications()
        self._update_tray_icon()
    
    def _update_tray_icon(self):
        """Update tray icon badge with notification count"""
        if not self.tray_icon:
            return
        
        unread_count = len([n for n in self.notifications if not n.read])
        if unread_count > 0:
            self.tray_icon.setToolTip(f"LaserFlow - {unread_count} unread notification(s)")
        else:
            self.tray_icon.setToolTip("LaserFlow - No notifications")
    
    def add_notification(self, title: str, message: str, notification_type: str = "info", duration: int = 5000) -> Notification:
        """Add a new notification"""
        notification = Notification(title, message, notification_type, duration)
        self.notifications.insert(0, notification)  # Add to beginning
        
        # Limit notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
        
        # Show system tray notification
        if self.tray_icon and self.tray_icon.isVisible():
            icon_type = {
                "info": QSystemTrayIcon.Information,
                "warning": QSystemTrayIcon.Warning,
                "error": QSystemTrayIcon.Critical,
                "success": QSystemTrayIcon.Information
            }.get(notification_type, QSystemTrayIcon.Information)
            
            self.tray_icon.showMessage(
                title,
                message,
                icon_type,
                duration
            )
        
        self._save_notifications()
        self._update_tray_icon()
        self.notification_added.emit(notification)
        
        return notification
    
    def mark_as_read(self, notification: Notification):
        """Mark notification as read"""
        notification.read = True
        self._save_notifications()
        self._update_tray_icon()
    
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification.read = True
        self._save_notifications()
        self._update_tray_icon()
    
    def remove_notification(self, notification: Notification):
        """Remove a notification"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self._save_notifications()
            self._update_tray_icon()
            self.notification_removed.emit(str(id(notification)))
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return len([n for n in self.notifications if not n.read])
    
    def get_recent_notifications(self, limit: int = 10) -> List[Notification]:
        """Get recent notifications"""
        return self.notifications[:limit]
    
    def _save_notifications(self):
        """Save notifications to file"""
        try:
            data = []
            for n in self.notifications:
                data.append({
                    "title": n.title,
                    "message": n.message,
                    "type": n.type,
                    "duration": n.duration,
                    "created_at": n.created_at.isoformat(),
                    "read": n.read
                })
            
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving notifications: {e}")
    
    def _load_notifications(self):
        """Load notifications from file"""
        if not self.db_path.exists():
            return
        
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.notifications = []
            for item in data:
                notification = Notification(
                    item.get("title", ""),
                    item.get("message", ""),
                    item.get("type", "info"),
                    item.get("duration", 5000)
                )
                notification.created_at = datetime.fromisoformat(item.get("created_at", datetime.now().isoformat()))
                notification.read = item.get("read", False)
                self.notifications.append(notification)
            
            self._update_tray_icon()
        except Exception as e:
            print(f"Error loading notifications: {e}")
    
    def schedule_notification(self, title: str, message: str, delay_seconds: int, notification_type: str = "info"):
        """Schedule a notification for later"""
        def show_notification():
            self.add_notification(title, message, notification_type)
        
        QTimer.singleShot(delay_seconds * 1000, show_notification)
    
    def cleanup_old_notifications(self, days: int = 7):
        """Remove notifications older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.notifications = [n for n in self.notifications if n.created_at > cutoff_date]
        self._save_notifications()
        self._update_tray_icon()
