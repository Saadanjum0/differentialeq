from flask import Flask, render_template, request, jsonify, session, send_from_directory
# Conditionally import matplotlib only when needed
import os
import secrets
import io
import base64
import re
import logging
from logging.handlers import RotatingFileHandler
from sympy import symbols, diff, sympify, solve, Eq, Add, Function, sin, exp
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities.lambdify import lambdify
import numpy as np
import sys
from dotenv import load_dotenv
import datetime
from logging_config import setup_logging, log_error, log_request

# Import matplotlib early to ensure it's available
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: Matplotlib not available. Plotting functionality will be limited.")

# Load environment variables
load_dotenv()

# Check if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL_ENV', False)

# Conditionally import flask_talisman
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False

# Conditionally import flask_limiter
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False

# Conditionally import flask_cors
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

app = Flask(__name__)

# Set up logging
setup_logging(app)

# Configure logging
if not IS_VERCEL:  # Skip file logging on serverless environments
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Differential Equation Analyzer startup')

# Security configurations
# Generate a strong secret key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Initialize Talisman for security headers if available
if TALISMAN_AVAILABLE and not IS_VERCEL:
    talisman = Talisman(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "https://polyfill.io", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", "data:"],
            'font-src': ["'self'"],
        },
        force_https=True,  # Force HTTPS
        strict_transport_security=True,
        session_cookie_secure=True,
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
        }
    )

# Initialize CORS if available
if CORS_AVAILABLE:
    CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize rate limiter if available
if LIMITER_AVAILABLE:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get("REDIS_URL", "memory://"),
        strategy="fixed-window"
    )

# Known cases removed as requested

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_linearity', methods=['POST'])
def check_linearity():
    """Check if a differential equation is linear"""
    # Get the equation from the form
    equation = request.form.get('equation', '')
    
    if not equation:
        return jsonify({
            'status': 'error',
            'message': 'Please enter a differential equation.'
        })
    
    # Check if the equation is linear
    if is_linear_de(equation):
        return jsonify({
            'status': 'success',
            'message': f"The differential equation '{equation}' is linear."
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f"The differential equation '{equation}' is not linear."
        })

@app.route('/verify_solution', methods=['POST'])
def verify_solution():
    """Verify if a function is a solution to a differential equation"""
    # Get the differential equation and solution from the form
    de = request.form.get('de', '')
    solution = request.form.get('solution', '')
    
    if not de or not solution:
        return jsonify({
            'status': 'error',
            'message': 'Please enter both the differential equation and the proposed solution.'
        })
    
    # Verify the solution
    result = verify_simple_solution(de, solution)
    
    # Always generate a plot, even if the solution is not valid
    plot_url = generate_solution_plot(de, solution)
    
    if result['is_valid']:
        return jsonify({
            'status': 'success',
            'message': f"The function '{solution}' is a valid solution to the differential equation '{de}'.",
            'plot_url': plot_url
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f"The function '{solution}' is not a valid solution to the differential equation '{de}'. {result.get('reason', '')}",
            'plot_url': plot_url  # Include plot URL even for invalid solutions
        })

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
    
    print(f"Normalized equation: {normalized}")
    return normalized

def is_linear_de(equation):
    """
    Determine if a differential equation is linear using a hybrid approach.
    
    This function uses both pattern matching and SymPy symbolic analysis:
    1. First performs fast pattern matching to identify obvious non-linear terms
    2. Then applies rigorous symbolic mathematics using SymPy for more complex cases
    
    A differential equation is linear if it can be written in the form:
    a₀(x)y + a₁(x)y' + a₂(x)y'' + ... + aₙ(x)y^(n) = f(x)
    
    Where all coefficients a₀(x), a₁(x), etc. are functions of x only (not involving y).
    
    Key properties that make an equation NON-linear include:
    1. Any term with y or its derivatives raised to a power other than 1
    2. Products of y or its derivatives (like y*y' or y'*y'')
    3. Transcendental functions of y (like sin(y), e^y, etc.)
    4. Rational expressions with y in the denominator
    """
    print(f"\nAnalyzing equation: {equation}")
    
    # STEP 1: Clean and normalize the equation
    # ----------------------------------------
    # Replace unicode prime symbols with standard notation
    equation = equation.replace('′', "'")
    
    # STEP 2: Direct pattern matching for obvious non-linear terms
    # -----------------------------------------------------------
    # This is faster and more reliable than symbolic parsing for clear cases
    if _contains_nonlinear_patterns(equation):
        return False
        
    # STEP 3: Make sure it's actually a differential equation
    # -----------------------------------------------------
    if "y'" not in equation and "y′" not in equation:
        print("Not a differential equation: no derivatives found")
        return False
    
    # STEP 4: Symbolic mathematical analysis (if pattern matching is inconclusive)
    # ---------------------------------------------------------------------------
    try:
        if not _is_linear_symbolic_analysis(equation):
            return False
    except Exception as e:
        print(f"Symbolic analysis failed: {str(e)}")
        # If symbolic analysis fails, we rely on the pattern matching already done
    
    # If we get here and no non-linearity was detected, the equation is linear
    print("Equation is linear - all checks passed")
    return True


def _contains_nonlinear_patterns(equation):
    """
    Check if the equation contains obvious non-linear terms using pattern matching.
    
    This function uses fast string pattern matching (not SymPy) to quickly identify
    common non-linear structures without the overhead of symbolic computation.
    
    The patterns are organized into groups:
    - Basic terms involving y itself (powers, trig functions, etc.)
    - Terms involving first derivatives (y')
    - Terms involving second derivatives (y'')
    - Terms involving third derivatives (y''')
    
    Returns True if non-linear patterns are found.
    """
    # GROUP 1: Basic non-linear terms involving y itself
    basic_nonlinear = [
        "y**", "y^", "y*y",                # y raised to powers
        "sin(y)", "cos(y)", "tan(y)",      # trigonometric functions of y
        "exp(y)", "e^y", "e**y",           # exponential of y
        "log(y)", "ln(y)",                 # logarithmic terms
        "/y", "1/y",                       # rational expressions with y in denominator
    ]
    
    # GROUP 2: Non-linear terms involving first derivative
    first_derivative_nonlinear = [
        "y'**", "y'^", "y'*y'",            # y' raised to powers
        "sin(y')", "cos(y')", "tan(y')",   # trig functions of y'
        "exp(y')", "e^y'", "e**y'",        # exponential of y'
        "y*y'",                            # product of y and y'
    ]
    
    # GROUP 3: Non-linear terms involving second derivative
    second_derivative_nonlinear = [
        "y''**", "y''^", "y''*y''",        # y'' raised to powers
        "sin(y'')", "cos(y'')", "tan(y'')",# trig functions of y''
        "exp(y'')", "e^y''", "e**y''",     # exponential of y''
        "e^(y'')", "e**(y'')",             # alternative notation
        "y*y''", "y'*y''",                 # products with y''
    ]
    
    # GROUP 4: Non-linear terms involving third derivative
    third_derivative_nonlinear = [
        "y'''**", "y'''^", "y'''*y'''",    # y''' raised to powers
        "sin(y''')", "e^y'''",             # functions of y'''
        "y*y'''", "y'*y'''", "y''*y'''",   # products with y'''
    ]
    
    # Combine all pattern groups
    all_patterns = []
    all_patterns.extend(basic_nonlinear)
    all_patterns.extend(first_derivative_nonlinear)
    all_patterns.extend(second_derivative_nonlinear)
    all_patterns.extend(third_derivative_nonlinear)
    
    # Also check for patterns using unicode prime (′) instead of standard prime (')
    unicode_patterns = [p.replace("'", "′") for p in all_patterns]
    all_patterns.extend(unicode_patterns)
    
    # Check each pattern
    for pattern in all_patterns:
        if pattern in equation:
            print(f"Non-linear term detected: {pattern}")
            return True
            
    # No non-linear patterns found
    return False


def _is_linear_symbolic_analysis(equation):
    """
    Analyze the equation using SymPy's symbolic mathematics to determine linearity.
    
    This function provides a rigorous mathematical analysis using SymPy library to:
    1. Transform the equation into symbolic form
    2. Examine coefficients of derivatives
    3. Check for higher powers of dependent variable
    4. Detect transcendental functions applied to dependent variable
    
    Returns True if the equation is found to be linear.
    """
    from sympy import symbols, Function, diff, sin, exp
    
    # Create symbolic variables and function
    x = symbols('x')
    y = Function('y')(x)
    
    # Normalize the equation to standard form: expression = 0
    if '=' in equation:
        lhs, rhs = equation.split('=', 1)
        eq_str = f"({lhs.strip()}) - ({rhs.strip()})"
    else:
        eq_str = equation.strip()
        
    # Step 1: Convert to SymPy syntax
    # -------------------------------
    # Replace derivatives with proper SymPy notation
    eq_str = eq_str.replace("y'''", "Derivative(y(x), x, 3)")
    eq_str = eq_str.replace("y''", "Derivative(y(x), x, 2)")
    eq_str = eq_str.replace("y'", "Derivative(y(x), x)")
    
    # Replace standalone y with y(x) function notation
    eq_str = re.sub(r'(?<![a-zA-Z0-9_])y(?![a-zA-Z0-9_\(])', 'y(x)', eq_str)
    
    # Replace power notation
    eq_str = eq_str.replace('^', '**')
    
    print(f"Symbolic form: {eq_str}")
    
    # Step 2: Parse the equation into a symbolic expression
    # ---------------------------------------------------
    try:
        expr = parse_expr(eq_str, local_dict={'y': y, 'x': x, 'Derivative': diff})
        
        # Step 3: Check linearity conditions
        # ---------------------------------
        
        # Create a list of y and all its derivatives to check
        derivatives = [y]  # y itself
        for i in range(1, 4):  # Add first, second, and third derivatives
            derivatives.append(diff(y, x, i))
            
        # Check 1: No variable coefficient for derivatives
        # ----------------------------------------------
        # For a linear DE, coefficients of derivatives must not contain y or its derivatives
        for deriv in derivatives:
            if expr.has(deriv):
                try:
                    # Collect terms with respect to this derivative
                    collected = expr.collect(deriv)
                    
                    # Get the coefficient of the derivative
                    coeff = collected.coeff(deriv)
                    
                    # Check if coefficient contains y or any derivative
                    if any(str(d) in str(coeff) for d in derivatives):
                        print(f"Non-linear: coefficient of {deriv} contains y or its derivatives")
                        return False
                except Exception as e:
                    print(f"Error analyzing coefficients: {e}")
                    # Be conservative - if we can't analyze, assume non-linear
                    return False
                    
        # Check 2: No higher powers of derivatives
        # --------------------------------------
        for deriv in derivatives:
            # Check for terms like (y')² or y'·y'
            if expr.has(deriv**2) or expr.has(deriv*deriv):
                print(f"Non-linear: found squared term {deriv}")
                return False
                
        # Check 3: No transcendental functions applied to y or derivatives
        # -------------------------------------------------------------
        for func in [sin, exp]:  # Check common functions
            for deriv in derivatives:
                if expr.has(func(deriv)):
                    print(f"Non-linear: found {func.__name__} of {deriv}")
                    return False
        
        # Equation passed all symbolic checks for linearity
        return True
        
    except Exception as e:
        print(f"Parsing error in symbolic analysis: {e}")
        # Could not analyze symbolically, rely on string pattern matching
        return True  # Return True as we already checked patterns

def verify_simple_solution(de, solution):
    """Verify if a function is a solution to a differential equation"""
    # Normalize inputs for comparison
    normalized_de = normalize_equation(de)
    
    # Call the core verification algorithm
    try:
        result = verify_with_sympy(de, solution)
        return result
    except Exception as e:
        print(f"Verification algorithm failed with error: {str(e)}")
        return {
            'is_valid': False,
            'reason': f"Verification failed. The algorithm couldn't determine if this is a valid solution. Error: {str(e)}"
        }

def verify_with_sympy(de, solution):
    """Verify if a solution satisfies a differential equation using SymPy
    
    Uses symbolic math to:
    1. Parse the solution expression
    2. Compute necessary derivatives
    3. Substitute into the original equation
    4. Check if the equation is satisfied at multiple points
    """
    try:
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
            print(f"Parsed solution: {y_solution}")
        except Exception as e:
            print(f"Failed to parse solution: {e}")
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
            print(f"Substituted equation: {eq_expr}")
        except Exception as e:
            print(f"Error parsing equation with substitutions: {e}")
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
                print(f"At x={point}: {value}")
                
                if abs(value) < 1e-6:  # Close enough to zero
                    valid_points += 1
                else:
                    if invalid_point is None:
                        invalid_point = point
                        invalid_value = value
            except Exception as e:
                print(f"Evaluation error at x={point}: {e}")
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
                
    except Exception as e:
        print(f"Error in verification process: {e}")
        return {
            'is_valid': False,
            'reason': f"Verification error: {e}"
        }

def generate_solution_plot(de, solution):
    """Generate a plot for the solution of the differential equation"""
    # Check if matplotlib is available
    if not MATPLOTLIB_AVAILABLE:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"
    
    # Default base64 image to return if plotting fails or matplotlib is not available
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
        # Replace common constants with numeric values
        for const in ['C', 'C1', 'C2']:
            if const in y_expr_clean:
                y_expr_clean = y_expr_clean.replace(const, '1')  # Use 1 as default value
        
        # Now parse the expression with numeric constants
        try:
            y_sym = parse_expr(y_expr_clean)
            print(f"Parsed solution for plotting: {y_sym}")
        except Exception as e:
            print(f"Error parsing solution for plotting: {e}")
            
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
            y_func = lambdify(x_sym, y_sym, modules=['numpy'])
        except Exception as e:
            print(f"Error creating numerical function: {e}")
            
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
            print(f"Error calculating function values: {calc_error}")
            
            # Create a simplified plot just with the equation
            plt.figure(figsize=(8, 5))
            plt.text(0.5, 0.5, f"Could not plot: {y_expr}\nError: {str(calc_error)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.tight_layout()
            
            # Save the error plot
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return f"data:image/png;base64,{plot_url}"
            
    except Exception as e:
        print(f"Error generating plot: {e}")
        
        # Create a fallback error plot
        if MATPLOTLIB_AVAILABLE:
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
        
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4//8/AAX+Av7czFnnAAAAAElFTkSuQmCC"

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
    })

# Request logging middleware
@app.before_request
def before_request():
    app.logger.info(f"Incoming {request.method} request to {request.url}")

@app.after_request
def after_request(response):
    log_request(app, request, response)
    return response

# Add error handlers
@app.errorhandler(404)
def not_found_error(error):
    log_error(app, error, "404 Not Found")
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    log_error(app, error, "500 Internal Server Error")
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(error):
    log_error(app, error, "Unhandled Exception")
    return render_template('errors/error.html',
                         error_code="500",
                         error_title="Internal Server Error",
                         error_description="An unexpected error occurred.",
                         error_color="#dc3545"), 500

# Add this at the end of the file
# Handler for Vercel serverless function
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path == "":
        return render_template('index.html')
    return app.send_static_file(path)

# For Vercel deployment
if __name__ == '__main__':
    # Check if running on Vercel
    if os.environ.get('VERCEL_ENV'):
        # In Vercel, we don't need to run the app
        # It will be handled by the serverless function
        pass
    else:
        # For local development
        port = int(os.environ.get('PORT', 5001))
        app.run(debug=True, host='0.0.0.0', port=port) 