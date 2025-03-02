# Differential Equation Analyzer

A web application for analyzing, solving, and visualizing differential equations. This application provides tools for checking linearity, verifying solutions, and visualizing differential equations.

## Features

- **Linearity Checker**: Determine if a differential equation is linear or non-linear
- **Solution Verifier**: Check if a function is a solution to a given differential equation
- **Visualization**: Plot solutions to differential equations
- **API Endpoints**: Access the functionality programmatically

## Local Development Setup

### Prerequisites

- Python 3.9
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
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

4. Run the application:
   ```
   ./run_app_simple.sh
   ```
   
   Or directly with Python:
   ```
   python app.py
   ```

5. Access the application at: http://127.0.0.1:5001

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose

### Running with Docker

1. Build and start the container:
   ```
   ./docker-run.sh
   ```
   
   Or manually:
   ```
   docker-compose build
   docker-compose up -d
   ```

2. Access the application at: http://localhost:5001

3. View logs:
   ```
   docker-compose logs -f
   ```

4. Stop the container:
   ```
   docker-compose down
   ```

## Deployment Options

### Netlify

The application is configured for deployment on Netlify using the following files:
- `netlify.toml`: Configuration for build settings and redirects
- `netlify-build.sh`: Custom build script for Netlify

### Vercel

The application is configured for deployment on Vercel using the following files:
- `vercel.json`: Configuration for build settings and environment variables
- `vercel-build.sh`: Custom build script for Vercel
- `.vercel/project.json`: Project configuration for Vercel

## Example Equations to Try

- Linear first-order equation: `y' + 2*y = sin(x)`
- Non-linear equation: `y' = y^2 * sin(x)`
- Second-order linear equation: `y'' + 4*y = 0`

## API Usage

The application provides API endpoints for programmatic access:

- `/api/check_linearity`: Check if an equation is linear
- `/api/verify_solution`: Verify if a function is a solution to an equation
- `/api/visualize`: Generate visualization data for an equation

Example API request:
```
curl -X POST http://localhost:5001/api/check_linearity \
  -H "Content-Type: application/json" \
  -d '{"equation": "y\' + 2*y = sin(x)"}'
```

## License

[MIT License](LICENSE) 