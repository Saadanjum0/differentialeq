#!/usr/bin/env python3
import sys
import json
import re
import io
import base64
import numpy as np

# Conditionally import matplotlib only when needed
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    pass

from sympy import symbols, Function, diff, parse_expr, sympify

def normalize_equation(equation):
    """Normalize the equation for analysis"""
    # Clean up the equation
    normalized = equation.strip()
    
    # Make sure there's a right-hand side
    if "=" not in normalized:
        normalized = f"{normalized} = 0"
        
    # Parse to standard form: F(x,y,y',y'',...) = 0
    left_side, right_side = normalized.split("=", 1)
    normalized = f"{left_side.strip()} - ({right_side.strip()}) = 0"
    
    return normalized

def verify_solution(de, solution):
    """Verify if a function is a solution to a differential equation"""
    # Normalize inputs for comparison
    normalized_de = normalize_equation(de)
    
    # Call the core verification algorithm
    try:
        result = verify_with_sympy(de, solution)
        return result
    except Exception as e:
        return {
            'is_valid': False,
            'reason': f"Verification failed. The algorithm couldn't determine if this is a valid solution. Error: {str(e)}"
        }

def verify_with_sympy(de, solution):
    """Verify if a solution satisfies a differential equation using SymPy"""
    # Create symbols
    x = symbols('x')
    y_func = Function('y')(x)
    
    # Parse the solution
    if "y = " not in solution:
        return {
            'is_valid': False,
            'reason': "Solution must be in the form 'y = f(x)'"
        }
        
    y_expr = solution.split("y = ")[1].replace("^", "**").replace("e**", "exp")
    
    try:
        y_solution = parse_expr(y_expr)
    except Exception as e:
        return {
            'is_valid': False,
            'reason': "Could not parse the solution. Try using standard notation."
        }
        
    # Parse the differential equation
    if "=" not in de:
        de = f"{de} = 0"  # Add right side if missing
        
    lhs, rhs = de.split("=", 1)
    lhs = lhs.strip()
    rhs = rhs.strip()
    
    # Equation in standard form: lhs - rhs = 0
    eq_str = f"{lhs} - ({rhs})"
    
    # Replace derivatives with expressions containing the solution
    derivatives = {
        "y''": str(diff(y_solution, x, 2)),
        "y'": str(diff(y_solution, x)),
        "y": str(y_solution)
    }
    
    # Apply replacements from longest to shortest to avoid partial matches
    for old, new in sorted(derivatives.items(), key=lambda x: -len(x[0])):
        eq_str = eq_str.replace(old, f"({new})")
        
    # Convert to Python syntax and parse
    eq_str = eq_str.replace("^", "**")
    try:
        eq_expr = parse_expr(eq_str)
    except Exception as e:
        return {
            'is_valid': False,
            'reason': f"Could not evaluate the equation with your solution: {e}"
        }
        
    # Evaluate at multiple points
    test_points = [-2, -1, -0.5, 0, 0.5, 1, 2]
    valid_points = 0
    invalid_point = None
    invalid_value = None
    
    for point in test_points:
        try:
            value = float(eq_expr.subs(x, point))
            
            if abs(value) < 1e-6:  # Close enough to zero
                valid_points += 1
            else:
                if invalid_point is None:
                    invalid_point = point
                    invalid_value = value
        except Exception:
            continue
            
    # Determine if the solution is valid
    min_valid_points = 4  # Require at least 4 valid points
    
    if valid_points >= min_valid_points:
        return {
            'is_valid': True,
            'reason': f"Solution verified at {valid_points} different points."
        }
    else:
        reason = "Could not verify the solution at enough points."
        if invalid_point is not None:
            reason = f"The equation is not satisfied at x = {invalid_point}. Value: {invalid_value} ≠ 0"
            
        return {
            'is_valid': False,
            'reason': reason
        }

def generate_solution_plot(de, solution):
    """Generate a plot for the solution of the differential equation"""
    try:
        # Extract the solution function from the input
        if "y = " in solution:
            y_expr = solution.split("y = ")[1]
        else:
            y_expr = solution
        
        # Set up SymPy for parsing
        x_sym = symbols('x')
        
        # Parse the solution using SymPy
        y_expr_clean = y_expr.replace('^', '**').replace('e**', 'exp')
        
        # Handle constants by replacing them with numeric values for plotting
        for const in ['C', 'C1', 'C2']:
            if const in y_expr_clean:
                y_expr_clean = y_expr_clean.replace(const, '1')  # Use 1 as default value
        
        # Now parse the expression with numeric constants
        try:
            y_sym = parse_expr(y_expr_clean)
        except Exception as e:
            # Create a simplified error plot
            plt.figure(figsize=(8, 5))
            plt.text(0.5, 0.5, f"Could not parse: {y_expr}\nError: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.tight_layout()
            
            # Save the error message plot
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{plot_url}"
        
        # Create a numerical function from symbolic expression
        try:
            from sympy.utilities.lambdify import lambdify
            y_func = lambdify(x_sym, y_sym, modules=['numpy'])
        except Exception as e:
            # Create a simplified error plot
            plt.figure(figsize=(8, 5))
            plt.text(0.5, 0.5, f"Could not create plot function: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.tight_layout()
            
            # Save the error message plot
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{plot_url}"
        
        # Generate x values for plotting
        x = np.linspace(-5, 5, 500)
        
        try:
            # Try to evaluate the function
            y = y_func(x)
            
            # Handle NaN and infinities
            y = np.array(y, dtype=float)  # Convert to float array
            valid_indices = np.isfinite(y)
            
            if not np.any(valid_indices):
                raise ValueError("No valid points to plot - function may have singularities everywhere in this range")
                
            x_valid = x[valid_indices]
            y_valid = y[valid_indices]
            
            # Limit y values to a reasonable range for display
            y_max = 10
            display_indices = np.abs(y_valid) < y_max
            x_display = x_valid[display_indices]
            y_display = y_valid[display_indices]
            
            # Create the plot
            plt.figure(figsize=(8, 5))
            
            if len(x_display) > 0:
                plt.plot(x_display, y_display, linewidth=2.5, color='#2A93D5')
            else:
                plt.text(0.5, 0.5, "Function values out of displayable range", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes, fontsize=12)
            
            # Add singularity markers if detected
            singularities = []
            for i in range(len(x) - 1):
                if valid_indices[i] and not valid_indices[i + 1] or not valid_indices[i] and valid_indices[i + 1]:
                    singularities.append((x[i] + x[i+1]) / 2)
            
            for sing in singularities[:3]:  # Limit to 3 singularities to avoid clutter
                plt.axvline(x=sing, color='r', linestyle='--', alpha=0.5)
            
            if singularities:
                plt.axvline(x=singularities[0], color='r', linestyle='--', alpha=0.5, 
                            label='Singularity')
                plt.legend()
            
            # Make the plot more informative and attractive
            plt.title(f"Solution: {solution}", fontsize=14)
            plt.xlabel("x", fontsize=12)
            plt.ylabel("y", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)
            plt.axvline(x=0, color='k', linestyle='-', alpha=0.2)
            
            # Show differential equation on the plot
            plt.figtext(0.5, 0.01, f"DE: {de}", ha='center', fontsize=10)
            
            # Add some spacing around the plot
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save the plot to a bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            
            # Convert the buffer to a base64 string
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{plot_url}"
            
        except Exception as calc_error:
            # Create a simplified plot just with the equation
            plt.figure(figsize=(8, 5))
            plt.text(0.5, 0.5, f"Could not plot: {y_expr}\nError: {str(calc_error)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.tight_layout()
            
            # Save the error message plot
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{plot_url}"
            
    except Exception as e:
        # Create a fallback error plot
        plt.figure(figsize=(8, 5))
        plt.text(0.5, 0.5, f"Error generating plot: {str(e)}", 
                horizontalalignment='center', verticalalignment='center',
                transform=plt.gca().transAxes, fontsize=12)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{plot_url}"

def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            'status': 'error',
            'message': 'Both differential equation and solution must be provided'
        }))
        sys.exit(1)
    
    de = sys.argv[1]
    solution = sys.argv[2]
    
    try:
        # Verify the solution
        result = verify_solution(de, solution)
        
        # Generate a plot
        plot_url = generate_solution_plot(de, solution)
        
        if result['is_valid']:
            response = {
                'status': 'success',
                'message': f"The function '{solution}' is a valid solution to the differential equation '{de}'.",
                'plot_url': plot_url
            }
        else:
            response = {
                'status': 'error',
                'message': f"The function '{solution}' is not a valid solution to the differential equation '{de}'. {result.get('reason', '')}",
                'plot_url': plot_url
            }
        
        print(json.dumps(response))
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': f"Error verifying solution: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main() 