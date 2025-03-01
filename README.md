# Differential Equation Analyzer

A web application for analyzing differential equations, checking linearity, and verifying solutions.

## Features

- **Linearity Checker**: Determine if a differential equation is linear
- **Solution Verifier**: Check if a function is a solution to a differential equation
- **Visualization**: Generate plots of solutions
- **API Access**: RESTful API endpoints for programmatic access

## Deployment Options

This application is configured for deployment on multiple platforms:

### Vercel Deployment

1. Fork this repository
2. Connect to Vercel
3. Deploy with the following settings:
   - Build Command: `./build.sh`
   - Output Directory: `.vercel/output`
   - Install Command: `pip install -r requirements.txt`

### Netlify Deployment

1. Connect your GitHub repository to Netlify
2. Configure the build settings:
   - Build command: `./netlify-build.sh`
   - Publish directory: `static`
3. Deploy the site

## Local Development

To run the application locally:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/differential-equation-app.git
   cd differential-equation-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```
   ./run_app.sh
   ```
   
   Or for a simpler setup:
   ```
   ./run_app_simple.sh
   ```

5. Open your browser and navigate to `http://localhost:5000`

## API Documentation

The application provides the following API endpoints:

### Check Linearity

**Endpoint**: `/check_linearity`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "equation": "y'' + 3*y' + 2*y = sin(x)"
}
```

**Response**:
```json
{
  "is_linear": true,
  "explanation": "The equation is linear because...",
  "highest_derivative": 2
}
```

### Verify Solution

**Endpoint**: `/verify_solution`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "de": "y'' + y = 0",
  "solution": "sin(x)"
}
```

**Response**:
```json
{
  "is_solution": true,
  "explanation": "The function is a solution because...",
  "plot_url": "data:image/png;base64,..."
}
```

### Health Check

**Endpoint**: `/health`  
**Method**: GET  

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2023-06-01T12:34:56.789Z"
}
```

## Testing

Run the test suite with:

```
python -m unittest test_flask.py
```

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Mathematics**: SymPy for symbolic mathematics
- **Visualization**: Matplotlib for plotting
- **Deployment**: Vercel and Netlify with serverless functions

## Security Features

- HTTPS enforcement
- Content Security Policy
- Rate limiting
- Secure cookies
- Input validation

## License

MIT License

## Author

Created by Saad Anjum 