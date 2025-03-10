import os
import logging
import time
from logging.handlers import RotatingFileHandler
from flask import request as flask_request, g

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logging(app):
    """Configure logging for the application"""
    # Set up basic configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a file handler for detailed logs
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Create a file handler for errors only
    error_handler = RotatingFileHandler(
        'logs/error.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Add handlers to the app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    
    return app.logger

def log_request(app, request=None, response=None):
    """Log details about the current request
    
    Args:
        app: The Flask application instance
        request: The request object (optional)
        response: The response object (optional)
    """
    # Use the provided request or fall back to flask.request
    req = request if request is not None else flask_request
    
    # Skip logging for static files
    if req.path.startswith('/static'):
        return
    
    # Calculate request processing time if available
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
    else:
        duration = 0
    
    # Log request details
    status_code = response.status_code if response else ""
    app.logger.info(
        f"Request: {req.method} {req.path} "
        f"({req.remote_addr}) - "
        f"Status: {status_code} - "
        f"Duration: {duration:.4f}s"
    )
    
    # Return the response if provided
    return response

def log_error(app, error, status_code=500):
    """Log an error with details"""
    app.logger.error(
        f"Error {status_code}: {str(error)} - "
        f"URL: {flask_request.url} - "
        f"Method: {flask_request.method} - "
        f"IP: {flask_request.remote_addr}"
    ) 