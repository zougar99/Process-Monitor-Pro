"""
Performance Optimizer - محسّن الأداء
Comprehensive performance improvements for the antivirus application
"""

import os
import sys
import time
import threading
import hashlib
from collections import OrderedDict
from functools import lru_cache
import psutil


class ScanCache:
    """Intelligent scan cache with TTL"""
    
    def __init__(self, max_size=5000, ttl=3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.lock = threading.Lock()
    
    def get(self, file_hash):
        """Get cached result"""
        with self.lock:
            if file_hash in self.cache:
                entry = self.cache[file_hash]
                # Check if expired
                if time.time() - entry['timestamp'] < self.ttl:
                    # Move to end (most recently used)
                    self.cache.move_to_end(file_hash)
                    return entry['result']
                else:
                    # Expired, remove it
                    del self.cache[file_hash]
        return None
    
    def set(self, file_hash, result):
        """Cache scan result"""
        with self.lock:
            # Remove oldest if cache is full
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)  # Remove oldest
            
            self.cache[file_hash] = {
                'result': result,
                'timestamp': time.time()
            }
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
    
    def size(self):
        """Get cache size"""
        with self.lock:
            return len(self.cache)


class FilePriorityQueue:
    """Priority queue for scanning files (risky files first)"""
    
    RISKY_EXTENSIONS = {'.exe', '.dll', '.sys', '.bat', '.cmd', '.scr', '.vbs', '.js', '.ps1', '.msi', '.com', '.pif'}
    HIGH_RISK_PATHS = ['system32', 'syswow64', 'temp', 'appdata', 'downloads', 'startup']
    
    @staticmethod
    def get_priority(file_path):
        """Get priority for file (higher = scan first)"""
        priority = 0
        file_lower = file_path.lower()
        
        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in FilePriorityQueue.RISKY_EXTENSIONS:
            priority += 10
        
        # Check path
        for risky_path in FilePriorityQueue.HIGH_RISK_PATHS:
            if risky_path in file_lower:
                priority += 5
                break
        
        # Check file size (smaller files first for faster scanning)
        try:
            size = os.path.getsize(file_path)
            if size < 1024 * 1024:  # < 1MB
                priority += 2
            elif size > 100 * 1024 * 1024:  # > 100MB
                priority -= 5
        except:
            pass
        
        return priority
    
    @staticmethod
    def sort_files(file_list):
        """Sort files by priority"""
        return sorted(file_list, key=FilePriorityQueue.get_priority, reverse=True)


class MemoryManager:
    """Memory management and optimization"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.memory_threshold = 0.8  # 80% of available memory
        self.cleanup_interval = 300  # 5 minutes
    
    def get_memory_usage(self):
        """Get current memory usage percentage"""
        try:
            memory_info = self.process.memory_info()
            system_memory = psutil.virtual_memory()
            return memory_info.rss / system_memory.total
        except:
            return 0.0
    
    def should_cleanup(self):
        """Check if memory cleanup is needed"""
        return self.get_memory_usage() > self.memory_threshold
    
    def force_gc(self):
        """Force garbage collection"""
        import gc
        collected = gc.collect()
        return collected


class ThreadPool:
    """Thread pool for parallel operations"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.workers = []
        self.queue = []
        self.lock = threading.Lock()
        self.running = False
    
    def start(self):
        """Start thread pool"""
        self.running = True
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop thread pool"""
        self.running = False
    
    def submit(self, func, *args, **kwargs):
        """Submit task to pool"""
        with self.lock:
            self.queue.append((func, args, kwargs))
    
    def _worker(self):
        """Worker thread"""
        while self.running:
            with self.lock:
                if not self.queue:
                    time.sleep(0.1)
                    continue
                func, args, kwargs = self.queue.pop(0)
            
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error in thread pool: {e}")


class PerformanceProfiler:
    """Profile application performance"""
    
    def __init__(self):
        self.profiles = {}
        self.lock = threading.Lock()
    
    def start_profile(self, name):
        """Start profiling"""
        with self.lock:
            self.profiles[name] = {
                'start': time.time(),
                'calls': self.profiles.get(name, {}).get('calls', 0) + 1
            }
    
    def end_profile(self, name):
        """End profiling"""
        with self.lock:
            if name in self.profiles:
                elapsed = time.time() - self.profiles[name]['start']
                if 'total_time' not in self.profiles[name]:
                    self.profiles[name]['total_time'] = 0
                self.profiles[name]['total_time'] += elapsed
                return elapsed
        return 0
    
    def get_stats(self):
        """Get performance statistics"""
        with self.lock:
            stats = {}
            for name, data in self.profiles.items():
                calls = data.get('calls', 0)
                total = data.get('total_time', 0)
                stats[name] = {
                    'calls': calls,
                    'total_time': total,
                    'avg_time': total / calls if calls > 0 else 0
                }
            return stats


# Global instances
scan_cache = ScanCache()
memory_manager = MemoryManager()
performance_profiler = PerformanceProfiler()
