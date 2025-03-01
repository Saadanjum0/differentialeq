# Differential Equation Analyzer API Documentation

This document provides detailed information about the API endpoints available in the Differential Equation Analyzer.

## Base URL

For local development:
```
http://localhost:5001
```

For production:
```
https://your-app-name.netlify.app
```

## Authentication

Currently, the API is open and does not require authentication.

## Endpoints

### 1. Check Linearity

Determines if a differential equation is linear.

**Endpoint:** `/check_linearity`  
**Method:** `POST`  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
- `equation` (string, required): The differential equation to check

**Example Request:**
```bash
curl -X POST \
  http://localhost:5001/check_linearity \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'equation=y%27%20%2B%202*y%20%3D%20sin(x)'
```

**Success Response:**
```json
{
  "status": "success",
  "message": "The differential equation 'y' + 2*y = sin(x)' is linear."
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error analyzing equation: Invalid syntax"
}
```

### 2. Verify Solution

Verifies if a function is a solution to a differential equation.

**Endpoint:** `/verify_solution`  
**Method:** `POST`  
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
- `de` (string, required): The differential equation
- `solution` (string, required): The proposed solution

**Example Request:**
```bash
curl -X POST \
  http://localhost:5001/verify_solution \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'de=y%27%20%2B%202*y%20%3D%20sin(x)&solution=y%20%3D%20e%5E(-2*x)%20*%20(C%20%2B%200.5*sin(x)%20-%200.5*cos(x))'
```

**Success Response:**
```json
{
  "status": "success",
  "message": "The function is a solution to the differential equation.",
  "plot_url": "data:image/png;base64,..."
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error verifying solution: Invalid solution format"
}
```

### 3. Health Check

Checks the health status of the application.

**Endpoint:** `/health`  
**Method:** `GET`

**Example Request:**
```bash
curl http://localhost:5001/health
```

**Success Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-03-01T12:34:56.789Z"
}
```

## Error Handling

The API uses standard HTTP response codes:

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "status": "error",
  "message": "Description of the error"
}
```

## Rate Limiting

- 100 requests per minute per IP address
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Plotting Parameters

When solutions are plotted, the following parameters are used:

- x-range: [-10, 10]
- Number of points: 1000
- Multiple solution curves for different C values
- Grid lines enabled
- Axes labels included

## Best Practices

1. Always URL-encode equation strings
2. Include error handling in your client code
3. Cache successful responses when appropriate
4. Use appropriate timeout values for requests

## Examples

### Python Example
```python
import requests

def check_linearity(equation):
    response = requests.post(
        'http://localhost:5001/check_linearity',
        data={'equation': equation}
    )
    return response.json()

def verify_solution(de, solution):
    response = requests.post(
        'http://localhost:5001/verify_solution',
        data={'de': de, 'solution': solution}
    )
    return response.json()
```

### JavaScript Example
```javascript
async function checkLinearity(equation) {
    const response = await fetch('/check_linearity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `equation=${encodeURIComponent(equation)}`
    });
    return response.json();
}

async function verifySolution(de, solution) {
    const response = await fetch('/verify_solution', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `de=${encodeURIComponent(de)}&solution=${encodeURIComponent(solution)}`
    });
    return response.json();
}
```

## Support

For API support, please:
1. Check the documentation
2. Search existing issues
3. Open a new issue if needed

## Changelog

### Version 1.0.0
- Initial API release
- Basic linearity checking
- Solution verification with plotting
- Health check endpoint 