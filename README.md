# Differential Equation Analyzer

A web application for analyzing differential equations, checking linearity, and verifying solutions.

## Features

- **Linearity Checker**: Determine if a differential equation is linear
- **Solution Verifier**: Check if a function is a solution to a differential equation
- **Visualization**: Generate plots of solutions

## Deployment on Netlify

This application is configured for deployment on Netlify using serverless functions.

### Deployment Steps

1. Connect your GitHub repository to Netlify
2. Configure the build settings:
   - Build command: `npm run build`
   - Publish directory: `static`
3. Deploy the site

### Local Development

To run the application locally:

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. For Netlify Functions development, install the Netlify CLI:
   ```
   npm install netlify-cli -g
   ```

4. Run the Netlify development server:
   ```
   netlify dev
   ```

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with SymPy for symbolic mathematics
- **Deployment**: Netlify with serverless functions

## License

MIT License

## Author

Created by Saad Anjum 