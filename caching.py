from functools import wraps
from flask import request, make_response
import hashlib
import json
import os
import time
from datetime import datetime, timedelta

class Cache:
    """Simple file-based cache implementation."""
    
    def __init__(self, cache_dir='cache', default_timeout=300):
        """Initialize the cache with a directory and default timeout."""
        self.cache_dir = cache_dir
        self.default_timeout = default_timeout
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, key_parts):
        """Generate a cache key from the provided parts."""
        if isinstance(key_parts, str):
            key_parts = [key_parts]
        
        # Convert all parts to strings and join
        key_str = '_'.join(str(part) for part in key_parts)
        
        # Create an MD5 hash of the key
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get(self, key):
        """Retrieve a value from the cache."""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if the cache has expired
            if data['expires_at'] < time.time():
                os.remove(cache_path)
                return None
            
            return data['value']
        except (json.JSONDecodeError, KeyError, IOError):
            return None
    
    def set(self, key, value, timeout=None):
        """Store a value in the cache."""
        if timeout is None:
            timeout = self.default_timeout
        
        cache_path = self._get_cache_path(key)
        
        data = {
            'value': value,
            'expires_at': time.time() + timeout
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            return True
        except IOError:
            return False
    
    def delete(self, key):
        """Remove a value from the cache."""
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except IOError:
                return False
        return False
    
    def clear(self):
        """Clear all cached values."""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except IOError:
                    continue
    
    def cleanup(self):
        """Remove expired cache entries."""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.cache'):
                cache_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_path, 'r') as f:
                        data = json.load(f)
                    
                    if data['expires_at'] < time.time():
                        os.remove(cache_path)
                except (json.JSONDecodeError, KeyError, IOError):
                    continue

def cached(timeout=300):
    """Decorator to cache function results."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = [f.__name__]
            cache_key.extend(args)
            cache_key.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            # Add request-specific data for API endpoints
            if request:
                cache_key.append(request.path)
                cache_key.append(request.method)
                cache_key.extend(f"{k}={v}" for k, v in sorted(request.args.items()))
            
            # Initialize cache
            cache = Cache()
            
            # Try to get cached response
            cached_value = cache.get(cache._get_cache_key(cache_key))
            if cached_value is not None:
                return cached_value
            
            # If not cached, call the function
            value = f(*args, **kwargs)
            
            # Cache the result
            cache.set(cache._get_cache_key(cache_key), value, timeout)
            
            return value
        return decorated_function
    return decorator

def setup_cache_cleanup(app, interval=3600):
    """Set up periodic cache cleanup."""
    def cleanup_task():
        while True:
            cache = Cache()
            cache.cleanup()
            time.sleep(interval)
    
    from threading import Thread
    cleanup_thread = Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()

# Example usage:
"""
@app.route('/api/data')
@cached(timeout=300)  # Cache for 5 minutes
def get_data():
    # Expensive operation here
    return jsonify(result)
""" 