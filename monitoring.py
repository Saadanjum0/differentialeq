import time
from functools import wraps
from flask import request, g
import logging
import psutil
import os

def setup_monitoring(app):
    """Set up performance monitoring for the Flask application."""
    
    # Create a logger for monitoring
    monitor_logger = logging.getLogger('monitoring')
    monitor_logger.setLevel(logging.INFO)
    
    # Create a file handler
    if not os.path.exists('logs'):
        os.makedirs('logs')
    handler = logging.FileHandler('logs/monitoring.log')
    handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )
    handler.setFormatter(formatter)
    monitor_logger.addHandler(handler)
    
    def log_performance_metrics():
        """Log system performance metrics."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        monitor_logger.info(
            f"Performance Metrics:\n"
            f"CPU Usage: {cpu_percent}%\n"
            f"Memory Usage: {memory.percent}%\n"
            f"Disk Usage: {disk.percent}%"
        )
    
    def monitor_request_performance(response):
        """Log request performance metrics."""
        if hasattr(g, 'start_time'):
            elapsed_time = time.time() - g.start_time
            monitor_logger.info(
                f"Request Performance:\n"
                f"Path: {request.path}\n"
                f"Method: {request.method}\n"
                f"Time: {elapsed_time:.3f}s\n"
                f"Status: {response.status_code}"
            )
        return response
    
    def start_request_timer():
        """Start timing the request."""
        g.start_time = time.time()
    
    # Register the monitoring functions
    app.before_request(start_request_timer)
    app.after_request(monitor_request_performance)
    
    # Schedule periodic performance logging
    def periodic_monitoring():
        """Log performance metrics periodically."""
        while True:
            log_performance_metrics()
            time.sleep(300)  # Log every 5 minutes
    
    # Start periodic monitoring in a background thread
    from threading import Thread
    monitoring_thread = Thread(target=periodic_monitoring, daemon=True)
    monitoring_thread.start()
    
    return monitor_logger

def monitor_function(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        # Log function performance
        logger = logging.getLogger('monitoring')
        logger.info(
            f"Function Performance:\n"
            f"Name: {func.__name__}\n"
            f"Time: {elapsed_time:.3f}s"
        )
        
        return result
    return wrapper

def get_system_health():
    """Get system health metrics."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu_usage': cpu_percent,
        'memory_usage': memory.percent,
        'disk_usage': disk.percent,
        'timestamp': time.time()
    }

class PerformanceMonitor:
    """Class to handle performance monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self.requests_served = 0
        self.errors_count = 0
        self.response_times = []
    
    def record_request(self, response_time, is_error=False):
        """Record a request's performance metrics."""
        self.requests_served += 1
        self.response_times.append(response_time)
        if is_error:
            self.errors_count += 1
    
    def get_statistics(self):
        """Get performance statistics."""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        uptime = time.time() - self.start_time
        
        return {
            'uptime': uptime,
            'requests_served': self.requests_served,
            'errors_count': self.errors_count,
            'error_rate': (self.errors_count / self.requests_served * 100) if self.requests_served > 0 else 0,
            'avg_response_time': avg_response_time,
            'system_health': get_system_health()
        } 