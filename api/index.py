from flask import Flask
# Initialize matplotlib with Agg backend before importing app
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for serverless environment

# Now import the app
from app import app

# This file is used by Vercel to handle serverless functions
# It uses the WSGI adapter pattern for Flask applications

def handler(request, context):
    """
    Vercel serverless function handler for Flask app
    This function adapts the Vercel serverless environment to work with Flask
    """
    from urllib.parse import urlparse
    
    # Create a WSGI environment from the request
    environ = {
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'REQUEST_METHOD': request.method,
        'PATH_INFO': urlparse(request.url).path,
        'QUERY_STRING': urlparse(request.url).query,
        'SERVER_NAME': 'vercel-serverless',
        'SERVER_PORT': '443',
        'HTTP_HOST': request.headers.get('host', 'vercel-serverless'),
        'VERCEL_ENV': 'true',  # Set environment variable for Vercel
    }
    
    # Add all HTTP headers
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            key = f'HTTP_{key}'
        environ[key] = value
    
    # Response data
    response_data = {}
    
    def start_response(status, response_headers, exc_info=None):
        status_code = int(status.split(' ')[0])
        response_data['statusCode'] = status_code
        response_data['headers'] = {k: v for k, v in response_headers}
    
    # Get response body from Flask app
    response_body = b''.join(app(environ, start_response))
    response_data['body'] = response_body.decode('utf-8')
    
    return response_data 