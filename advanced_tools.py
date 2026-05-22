"""
Advanced Tools - أدوات متقدمة موجودة في جميع تطبيقات مضاد الفيروسات
"""

import os
import json
import time
import threading
import schedule
from datetime import datetime
from pathlib import Path

# Multi-language support
try:
    from multi_language_support import PowerShellExecutor, BatchExecutor, SystemCommandExecutor
    MULTI_LANG_AVAILABLE = True
except ImportError:
    MULTI_LANG_AVAILABLE = False
    PowerShellExecutor = None
    BatchExecutor = None
    SystemCommandExecutor = None


class ScheduledScans:
    """Scheduled Scans Manager - فحوصات مجدولة"""
    
    def __init__(self, antivirus_engine):
        self.engine = antivirus_engine
        self.schedules = []
        self.schedule_file = "scan_schedules.json"
        self.load_schedules()
        self.running = False
    
    def load_schedules(self):
        """Load scheduled scans"""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    self.schedules = json.load(f)
            except:
                self.schedules = []
    
    def save_schedules(self):
        """Save scheduled scans"""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedules, f, indent=2)
        except:
            pass
    
    def add_schedule(self, scan_type, time_str, days=None):
        """Add scheduled scan"""
        schedule_entry = {
            'id': len(self.schedules) + 1,
            'type': scan_type,  # 'quick', 'full', 'custom'
            'time': time_str,  # 'HH:MM'
            'days': days or [],  # ['monday', 'tuesday', ...] or None for daily
            'enabled': True,
            'last_run': None,
            'next_run': None
        }
        self.schedules.append(schedule_entry)
        self.save_schedules()
        return schedule_entry
    
    def remove_schedule(self, schedule_id):
        """Remove scheduled scan"""
        self.schedules = [s for s in self.schedules if s['id'] != schedule_id]
        self.save_schedules()
    
    def start_scheduler(self):
        """Start scheduler thread"""
        if self.running:
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()


class WhitelistManager:
    """Whitelist/Blacklist Management"""
    
    def __init__(self):
        self.whitelist_file = "whitelist.json"
        self.blacklist_file = "blacklist.json"
        self.whitelist = set()
        self.blacklist = set()
        self.load_lists()
    
    def load_lists(self):
        """Load whitelist and blacklist"""
        # Whitelist
        if os.path.exists(self.whitelist_file):
            try:
                with open(self.whitelist_file, 'r') as f:
                    data = json.load(f)
                    self.whitelist = set(data.get('files', []))
            except:
                self.whitelist = set()
        
        # Blacklist
        if os.path.exists(self.blacklist_file):
            try:
                with open(self.blacklist_file, 'r') as f:
                    data = json.load(f)
                    self.blacklist = set(data.get('files', []))
            except:
                self.blacklist = set()
    
    def save_lists(self):
        """Save whitelist and blacklist"""
        # Whitelist
        try:
            with open(self.whitelist_file, 'w') as f:
                json.dump({'files': list(self.whitelist)}, f, indent=2)
        except:
            pass
        
        # Blacklist
        try:
            with open(self.blacklist_file, 'w') as f:
                json.dump({'files': list(self.blacklist)}, f, indent=2)
        except:
            pass
    
    def add_to_whitelist(self, file_path):
        """Add file to whitelist"""
        self.whitelist.add(file_path)
        self.save_lists()
    
    def add_to_blacklist(self, file_path):
        """Add file to blacklist"""
        self.blacklist.add(file_path)
        self.save_lists()
    
    def remove_from_whitelist(self, file_path):
        """Remove from whitelist"""
        self.whitelist.discard(file_path)
        self.save_lists()
    
    def remove_from_blacklist(self, file_path):
        """Remove from blacklist"""
        self.blacklist.discard(file_path)
        self.save_lists()
    
    def is_whitelisted(self, file_path):
        """Check if file is whitelisted"""
        return file_path in self.whitelist
    
    def is_blacklisted(self, file_path):
        """Check if file is blacklisted"""
        return file_path in self.blacklist


class USBProtection:
    """USB Protection - حماية USB"""
    
    def __init__(self, antivirus_engine):
        self.engine = antivirus_engine
        self.enabled = False
        self.auto_scan = True
        self.auto_quarantine = False
    
    def scan_usb_drive(self, drive_letter):
        """Scan USB drive"""
        drive_path = f"{drive_letter}:\\"
        if os.path.exists(drive_path):
            return self.engine.scan_directory(drive_path, recursive=True)
        return None
    
    def monitor_usb_devices(self):
        """Monitor for new USB devices"""
        # This would require platform-specific code
        # For Windows, could use WMI or registry monitoring
        pass


class BrowserProtection:
    """Browser Protection - حماية المتصفح"""
    
    def __init__(self):
        self.enabled = False
        self.blocked_domains = set()
        self.blocked_file = "blocked_domains.json"
        self.load_blocked_domains()
    
    def load_blocked_domains(self):
        """Load blocked domains"""
        if os.path.exists(self.blocked_file):
            try:
                with open(self.blocked_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_domains = set(data.get('domains', []))
            except:
                self.blocked_domains = set()
    
    def save_blocked_domains(self):
        """Save blocked domains"""
        try:
            with open(self.blocked_file, 'w') as f:
                json.dump({'domains': list(self.blocked_domains)}, f, indent=2)
        except:
            pass
    
    def add_blocked_domain(self, domain):
        """Add domain to blocklist"""
        self.blocked_domains.add(domain)
        self.save_blocked_domains()
    
    def is_blocked(self, domain):
        """Check if domain is blocked"""
        return domain in self.blocked_domains


class NetworkProtection:
    """Network Protection - حماية الشبكة"""
    
    def __init__(self):
        self.enabled = False
        self.blocked_ips = set()
        self.blocked_file = "blocked_ips.json"
        self.load_blocked_ips()
    
    def load_blocked_ips(self):
        """Load blocked IPs"""
        if os.path.exists(self.blocked_file):
            try:
                with open(self.blocked_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_ips = set(data.get('ips', []))
            except:
                self.blocked_ips = set()
    
    def save_blocked_ips(self):
        """Save blocked IPs"""
        try:
            with open(self.blocked_file, 'w') as f:
                json.dump({'ips': list(self.blocked_ips)}, f, indent=2)
        except:
            pass
    
    def add_blocked_ip(self, ip):
        """Add IP to blocklist"""
        self.blocked_ips.add(ip)
        self.save_blocked_ips()
    
    def is_blocked(self, ip):
        """Check if IP is blocked"""
        return ip in self.blocked_ips


class PerformanceMonitor:
    """Performance Monitor - مراقبة الأداء"""
    
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'scan_speed': [],
            'threats_per_hour': []
        }
    
    def get_cpu_usage(self):
        """Get CPU usage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    def get_memory_usage(self):
        """Get memory usage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0
    
    def record_scan_metrics(self, files_scanned, duration):
        """Record scan metrics"""
        if duration > 0:
            speed = files_scanned / duration
            self.metrics['scan_speed'].append(speed)
            # Keep only last 100 entries
            if len(self.metrics['scan_speed']) > 100:
                self.metrics['scan_speed'] = self.metrics['scan_speed'][-100:]


class DatabaseUpdater:
    """Database Updater - تحديث قاعدة البيانات"""
    
    def __init__(self, threat_database):
        self.threat_db = threat_database
        self.last_update = None
        self.update_file = "last_update.json"
        self.load_update_info()
    
    def load_update_info(self):
        """Load update information"""
        if os.path.exists(self.update_file):
            try:
                with open(self.update_file, 'r') as f:
                    data = json.load(f)
                    self.last_update = data.get('last_update')
            except:
                self.last_update = None
    
    def save_update_info(self):
        """Save update information"""
        try:
            with open(self.update_file, 'w') as f:
                json.dump({'last_update': datetime.now().isoformat()}, f, indent=2)
            self.last_update = datetime.now().isoformat()
        except:
            pass
    
    def check_for_updates(self):
        """Check for database updates"""
        # In production, this would connect to update server
        # For now, just mark as updated
        self.save_update_info()
        return True
    
    def update_database(self):
        """Update threat database"""
        # In production, download latest signatures
        # For now, just mark as updated
        self.save_update_info()
        return True


class SystemCleanup:
    """System Cleanup - تنظيف النظام"""
    
    def __init__(self):
        self.cleanup_history = []
    
    def clean_temp_files(self):
        """Clean temporary files"""
        cleaned = 0
        temp_dirs = [
            os.path.expanduser("~/AppData/Local/Temp"),
            "C:\\Windows\\Temp",
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                cleaned += 1
                        except:
                            pass
                except:
                    pass
        
        return cleaned
    
    def clean_browser_cache(self):
        """Clean browser cache"""
        # This would require browser-specific paths
        return 0
    
    def optimize_system(self):
        """Optimize system performance"""
        # Placeholder for system optimization
        return True


class LogViewer:
    """Log Viewer - عرض السجلات"""
    
    def __init__(self):
        self.log_file = "antivirus.log"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
    
    def log(self, level, message):
        """Log message"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Rotate log if too large
            if os.path.getsize(self.log_file) > self.max_log_size:
                self.rotate_log()
        except:
            pass
    
    def rotate_log(self):
        """Rotate log file"""
        try:
            if os.path.exists(self.log_file):
                backup = f"{self.log_file}.old"
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(self.log_file, backup)
        except:
            pass
    
    def get_logs(self, lines=100):
        """Get recent logs"""
        if not os.path.exists(self.log_file):
            return []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except:
            return []


class BackupManager:
    """Backup Manager - إدارة النسخ الاحتياطي"""
    
    def __init__(self):
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_settings(self):
        """Backup application settings"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"settings_backup_{timestamp}.json")
        
        settings = {
            'threat_database': self._read_if_exists("threat_database.json"),
            'whitelist': self._read_if_exists("whitelist.json"),
            'blacklist': self._read_if_exists("blacklist.json"),
            'schedules': self._read_if_exists("scan_schedules.json"),
            'backup_date': datetime.now().isoformat()
        }
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return backup_path
        except:
            return None
    
    def restore_settings(self, backup_path):
        """Restore settings from backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            for key, value in settings.items():
                if key != 'backup_date' and value:
                    file_name = f"{key}.json"
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump(value, f, indent=2, ensure_ascii=False)
            
            return True
        except:
            return False
    
    def _read_if_exists(self, file_path):
        """Read file if exists"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None
    
    def list_backups(self):
        """List all backups"""
        backups = []
        if os.path.exists(self.backup_dir):
            for file in os.listdir(self.backup_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, file)
                    mtime = os.path.getmtime(file_path)
                    backups.append({
                        'file': file,
                        'path': file_path,
                        'date': datetime.fromtimestamp(mtime).isoformat()
                    })
        return sorted(backups, key=lambda x: x['date'], reverse=True)
