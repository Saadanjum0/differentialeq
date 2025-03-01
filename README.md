# Differential Equation Analyzer with Matplotlib Visualization

A web application for analyzing differential equations with visualization capabilities. This application provides two main features:

1. **Linearity Checker**: Determines if a given differential equation is linear or non-linear.
2. **Solution Verifier**: Verifies if a given function is a solution to a differential equation and visualizes the solution using Matplotlib.

## Features

- Check if a differential equation is linear
- Verify if a function is a solution to a differential equation
- Visualize solutions with Matplotlib plots
- Interactive examples to try

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: Matplotlib
- **Mathematical Processing**: SymPy, NumPy
- **Math Rendering**: MathJax

## Setup and Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd differential-equation-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Use

### Linearity Checker

1. Enter a differential equation in the input field (e.g., `y'' + 3y' + 2y = sin(x)`).
2. Click the "Check Linearity" button.
3. The result will show whether the equation is linear or non-linear.

### Solution Verifier

1. Enter a differential equation in the "Differential Equation" field (e.g., `y'' + y = 0`).
2. Enter a proposed solution in the "Proposed Solution" field (e.g., `y = sin(x)`).
3. Click the "Verify Solution" button.
4. The result will show whether the function is a solution to the differential equation.
5. If the solution is valid, a plot of the solution will be displayed.

### Examples

The application includes several examples that you can try:

- **Example 1**: A linear first-order differential equation
- **Example 2**: A linear second-order differential equation
- **Example 3**: A non-linear differential equation

Click the "Try this example" button to populate the input fields with the example.

## Limitations

- The application uses a simplified approach to check linearity and verify solutions.
- For solution verification, it relies on a predefined set of known cases and basic symbolic computation.
- Complex differential equations or solutions may not be correctly analyzed.
- The plotting functionality uses numerical evaluation and may not work for all mathematical expressions.

## Future Improvements

- Implement more robust symbolic computation for solution verification
- Add support for systems of differential equations
- Include step-by-step solution methods
- Provide more advanced visualization options (phase portraits, direction fields, etc.)
- Add the ability to solve differential equations numerically 