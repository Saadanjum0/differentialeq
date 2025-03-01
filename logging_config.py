import os
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logging(app):
    # Set up formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File handler for errors (error.log)
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # File handler for warnings and info (app.log)
    info_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Set up the app logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(info_handler)
    app.logger.addHandler(console_handler)

    # Remove default Flask handler
    app.logger.removeHandler(default_handler for default_handler in app.logger.handlers if isinstance(default_handler, logging.StreamHandler))

    # Log startup message
    app.logger.info('Application startup complete')

def log_error(app, error, error_type="Application Error"):
    """
    Log an error with full details
    """
    app.logger.error(
        f"{error_type}: {str(error)}\n"
        f"Error Type: {type(error).__name__}\n"
        f"Error Details: {str(error)}"
    )

def log_request(app, request, response=None):
    """
    Log HTTP request details
    """
    app.logger.info(
        f"Request: {request.method} {request.url}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Response Status: {response.status_code if response else 'No response'}"
    ) 