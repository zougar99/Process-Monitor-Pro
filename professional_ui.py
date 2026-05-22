"""
Professional UI Components
مكونات واجهة احترافية
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime


class AnimatedProgressBar:
    """Animated progress bar with smooth transitions"""
    
    def __init__(self, parent, width=400, height=20):
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='#2d2d2d', highlightthickness=0)
        self.width = width
        self.height = height
        self.progress = 0
        self.target_progress = 0
        self.animation_speed = 2
        
    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)
        self._draw()
    
    def _draw(self):
        """Draw progress bar"""
        self.canvas.delete("all")
        
        # Background
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill='#3d3d3d', outline='')
        
        # Progress fill with gradient effect
        progress_width = int(self.width * self.progress / 100)
        if progress_width > 0:
            # Main fill
            self.canvas.create_rectangle(0, 0, progress_width, self.height, 
                                       fill='#4CAF50', outline='')
            # Highlight
            self.canvas.create_rectangle(0, 0, progress_width, self.height // 3, 
                                       fill='#66BB6A', outline='')
        
        # Border
        self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                   outline='#555555', width=1)
        
        # Text
        text = f"{int(self.progress)}%"
        self.canvas.create_text(self.width // 2, self.height // 2, 
                              text=text, fill='#ffffff', font=('Arial', 9, 'bold'))
    
    def set_progress(self, value):
        """Set target progress - SAFE"""
        try:
            self.target_progress = max(0, min(100, value))
            self._animate()
        except:
            pass
    
    def _animate(self):
        """Animate progress - SAFE"""
        try:
            if abs(self.progress - self.target_progress) > 0.5:
                if self.progress < self.target_progress:
                    self.progress = min(self.progress + self.animation_speed, self.target_progress)
                else:
                    self.progress = max(self.progress - self.animation_speed, self.target_progress)
                self._draw()
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.after(10, self._animate)
        except:
            pass  # Stop animation on error


class StatusCard:
    """Professional status card component"""
    
    def __init__(self, parent, title, value, icon="", color='#4CAF50', width=200, height=120):
        self.frame = tk.Frame(parent, bg='#2d2d2d', relief=tk.RAISED, bd=1)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.width = width
        self.height = height
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI elements"""
        # Icon and title frame (smaller)
        header_frame = tk.Frame(self.frame, bg='#2d2d2d')
        header_frame.pack(fill=tk.X, padx=8, pady=(8, 3))
        
        if self.icon:
            icon_label = tk.Label(header_frame, text=self.icon, bg='#2d2d2d', 
                                fg=self.color, font=('Arial', 12))
            icon_label.pack(side=tk.LEFT, padx=(0, 3))
        
        title_label = tk.Label(header_frame, text=self.title, bg='#2d2d2d', 
                              fg='#aaaaaa', font=('Arial', 8))
        title_label.pack(side=tk.LEFT)
        
        # Value (smaller font)
        self.value_label = tk.Label(self.frame, text=str(self.value), bg='#2d2d2d', 
                                   fg=self.color, font=('Arial', 18, 'bold'))
        self.value_label.pack(pady=5)
        
        # Hover effect
        self.frame.bind('<Enter>', lambda e: self._on_hover(True))
        self.frame.bind('<Leave>', lambda e: self._on_hover(False))
    
    def _on_hover(self, enter):
        """Handle hover effect"""
        if enter:
            self.frame.config(bg='#3d3d3d')
            for widget in self.frame.winfo_children():
                widget.config(bg='#3d3d3d')
        else:
            self.frame.config(bg='#2d2d2d')
            for widget in self.frame.winfo_children():
                widget.config(bg='#2d2d2d')
    
    def update_value(self, value):
        """Update card value - SAFE"""
        try:
            self.value = value
            if hasattr(self, 'value_label') and self.value_label:
                self.value_label.config(text=str(value))
        except Exception as e:
            pass  # Silently ignore errors
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)


class ProfessionalButton:
    """Professional button with hover effects"""
    
    def __init__(self, parent, text, command, icon="", style='primary'):
        self.style = style
        self.colors = {
            'primary': {'bg': '#2196F3', 'hover': '#1976D2', 'fg': '#ffffff'},
            'success': {'bg': '#4CAF50', 'hover': '#388E3C', 'fg': '#ffffff'},
            'danger': {'bg': '#f44336', 'hover': '#D32F2F', 'fg': '#ffffff'},
            'warning': {'bg': '#FF9800', 'hover': '#F57C00', 'fg': '#ffffff'},
            'info': {'bg': '#00BCD4', 'hover': '#0097A7', 'fg': '#ffffff'},
        }
        
        color = self.colors.get(style, self.colors['primary'])
        
        self.button = tk.Button(parent, text=f"{icon} {text}" if icon else text,
                              command=command, bg=color['bg'], fg=color['fg'],
                              font=('Arial', 10, 'bold'), relief=tk.FLAT,
                              cursor='hand2', padx=15, pady=8,
                              activebackground=color['hover'],
                              activeforeground=color['fg'])
        
        self.button.bind('<Enter>', lambda e: self.button.config(bg=color['hover']))
        self.button.bind('<Leave>', lambda e: self.button.config(bg=color['bg']))
    
    def pack(self, **kwargs):
        self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.button.grid(**kwargs)


class RealTimeStats:
    """Real-time statistics display"""
    
    def __init__(self, parent):
        self.parent = parent
        self.stats = {
            'files_scanned': 0,
            'threats_found': 0,
            'scan_speed': 0,
            'memory_usage': 0
        }
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.frame = tk.Frame(self.parent, bg='#1e1e1e')
        
        # Stats grid (smaller, more compact)
        stats_grid = tk.Frame(self.frame, bg='#1e1e1e')
        stats_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Files scanned (smaller cards)
        self.files_card = StatusCard(stats_grid, "Files Scanned", "0", "📁", '#2196F3', width=150, height=80)
        self.files_card.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        # Threats found
        self.threats_card = StatusCard(stats_grid, "Threats Found", "0", "⚠️", '#f44336', width=150, height=80)
        self.threats_card.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        # Scan speed
        self.speed_card = StatusCard(stats_grid, "Files/sec", "0", "⚡", '#FF9800', width=150, height=80)
        self.speed_card.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        # Memory usage
        self.memory_card = StatusCard(stats_grid, "Memory", "0 MB", "💾", '#9C27B0', width=150, height=80)
        self.memory_card.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
    
    def update_stats(self, files_scanned=0, threats_found=0, scan_speed=0, memory_usage=0):
        """Update statistics - FIXED with comprehensive error handling"""
        try:
            if hasattr(self, 'files_card') and self.files_card:
                try:
                    self.files_card.update_value(str(files_scanned))
                except:
                    pass
            if hasattr(self, 'threats_card') and self.threats_card:
                try:
                    self.threats_card.update_value(str(threats_found))
                except:
                    pass
            if hasattr(self, 'speed_card') and self.speed_card:
                try:
                    self.speed_card.update_value(f"{scan_speed:.1f}")
                except:
                    pass
            if hasattr(self, 'memory_card') and self.memory_card:
                try:
                    self.memory_card.update_value(f"{memory_usage:.1f} MB")
                except:
                    pass
        except Exception as e:
            # Silently handle all errors - prevent callback exceptions
            pass
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)


class NotificationPanel:
    """Professional notification panel"""
    
    def __init__(self, parent, max_notifications=5):
        self.parent = parent
        self.max_notifications = max_notifications
        self.notifications = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.frame = tk.Frame(self.parent, bg='#1e1e1e')
        self.canvas = tk.Canvas(self.frame, bg='#1e1e1e', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#1e1e1e')
        
        def safe_update_scrollregion(e):
            try:
                bbox = self.canvas.bbox("all")
                if bbox and len(bbox) == 4:
                    if all(isinstance(x, (int, float)) for x in bbox):
                        self.canvas.configure(scrollregion=bbox)
            except Exception:
                pass
        
        self.scrollable_frame.bind("<Configure>", safe_update_scrollregion)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_notification(self, message, type='info', duration=5000):
        """Add notification"""
        colors = {
            'info': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#f44336'
        }
        
        color = colors.get(type, colors['info'])
        
        notification_frame = tk.Frame(self.scrollable_frame, bg=color, relief=tk.RAISED, bd=1)
        notification_frame.pack(fill=tk.X, padx=5, pady=2)
        
        message_label = tk.Label(notification_frame, text=message, bg=color, 
                                fg='#ffffff', font=('Arial', 9), wraplength=300)
        message_label.pack(padx=10, pady=5)
        
        time_label = tk.Label(notification_frame, 
                            text=datetime.now().strftime("%H:%M:%S"), 
                            bg=color, fg='#ffffff', font=('Arial', 7))
        time_label.pack(padx=10, pady=(0, 5))
        
        self.notifications.append(notification_frame)
        
        # Remove old notifications
        if len(self.notifications) > self.max_notifications:
            old = self.notifications.pop(0)
            old.destroy()
        
        # Auto remove after duration
        if duration > 0:
            def safe_remove():
                try:
                    self._remove_notification(notification_frame)
                except:
                    pass
            self.parent.after(duration, safe_remove)
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def _remove_notification(self, notification_frame):
        """Remove notification"""
        if notification_frame in self.notifications:
            self.notifications.remove(notification_frame)
            notification_frame.destroy()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)


class ProfessionalHeader:
    """Professional header with branding - improved dark theme"""
    
    def __init__(self, parent, title, subtitle=""):
        self.frame = tk.Frame(parent, bg='#1f6feb', height=90)
        self.frame.pack_propagate(False)
        
        # Title - supports Arabic
        self.title_label = tk.Label(self.frame, text=title, bg='#1f6feb', 
                             fg='#ffffff', font=('Arial', 18, 'bold'))
        self.title_label.pack(pady=(12, 0))
        
        self.subtitle_label = None
        if subtitle:
            self.subtitle_label = tk.Label(self.frame, text=subtitle, bg='#1f6feb', 
                                     fg='#c9d1d9', font=('Arial', 10))
            self.subtitle_label.pack(pady=(0, 12))
    
    def update_text(self, title, subtitle=""):
        """Update title/subtitle for language switch"""
        self.title_label.config(text=title)
        if self.subtitle_label:
            self.subtitle_label.config(text=subtitle)
    
    def pack(self, **kwargs):
        self.frame.pack(fill=tk.X, **kwargs)


class ScanProgressIndicator:
    """Professional scan progress indicator"""
    
    def __init__(self, parent, ready_text="Ready to scan..."):
        self.frame = tk.Frame(parent, bg='#161b22')
        
        # Current file label
        self.current_file_label = tk.Label(self.frame, text=ready_text, 
                                         bg='#161b22', fg='#c9d1d9', 
                                         font=('Arial', 10))
        self.current_file_label.pack(pady=5)
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar(self.frame, width=600, height=25)
        self.progress_bar.pack(pady=5)
        
        # Stats
        self.stats_label = tk.Label(self.frame, text="Files: 0 | Threats: 0", 
                                   bg='#161b22', fg='#8b949e', font=('Arial', 9))
        self.stats_label.pack(pady=5)
    
    def set_label(self, ready_text):
        """Set ready/initial label for language switch"""
        if hasattr(self, 'current_file_label') and self.current_file_label:
            self.current_file_label.config(text=ready_text)
    
    def update_progress(self, progress, current_file="", files_scanned=0, threats_found=0):
        """Update progress - SAFE"""
        try:
            if hasattr(self, 'progress_bar') and self.progress_bar:
                self.progress_bar.set_progress(progress)
            if current_file and hasattr(self, 'current_file_label') and self.current_file_label:
                self.current_file_label.config(text=f"Scanning: {current_file[:60]}...")
            if hasattr(self, 'stats_label') and self.stats_label:
                self.stats_label.config(text=f"Files: {files_scanned} | Threats: {threats_found}")
        except Exception as e:
            pass  # Silently ignore errors
    
    def pack(self, **kwargs):
        self.frame.pack(fill=tk.X, **kwargs)
