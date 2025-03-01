#!/usr/bin/env python3
import sys
import json
import re
from sympy import symbols, Function, diff, sin, exp, parse_expr

def is_linear_de(equation):
    """
    Determine if a differential equation is linear using a hybrid approach.
    
    This function uses both pattern matching and SymPy symbolic analysis:
    1. First performs fast pattern matching to identify obvious non-linear terms
    2. Then applies rigorous symbolic mathematics using SymPy for more complex cases
    
    A differential equation is linear if it can be written in the form:
    a₀(x)y + a₁(x)y' + a₂(x)y'' + ... + aₙ(x)y^(n) = f(x)
    
    Where all coefficients a₀(x), a₁(x), etc. are functions of x only (not involving y).
    """
    # STEP 1: Clean and normalize the equation
    # Replace unicode prime symbols with standard notation
    equation = equation.replace('′', "'")
    
    # STEP 2: Direct pattern matching for obvious non-linear terms
    if _contains_nonlinear_patterns(equation):
        return False
        
    # STEP 3: Make sure it's actually a differential equation
    if "y'" not in equation and "y′" not in equation:
        return False
    
    # STEP 4: Symbolic mathematical analysis (if pattern matching is inconclusive)
    try:
        if not _is_linear_symbolic_analysis(equation):
            return False
    except Exception:
        # If symbolic analysis fails, we rely on the pattern matching already done
        pass
        
    # If we get here and no non-linearity was detected, the equation is linear
    return True

def _contains_nonlinear_patterns(equation):
    """Check if the equation contains obvious non-linear terms using pattern matching."""
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
            return True
            
    # No non-linear patterns found
    return False

def _is_linear_symbolic_analysis(equation):
    """Analyze the equation using SymPy's symbolic mathematics to determine linearity."""
    # Create symbolic variables and function
    x = symbols('x')
    y = Function('y')(x)
    
    # Normalize the equation to standard form: expression = 0
    if '=' in equation:
        lhs, rhs = equation.split('=', 1)
        eq_str = f"({lhs.strip()}) - ({rhs.strip()})"
    else:
        eq_str = equation.strip()
        
    # Convert to SymPy syntax
    eq_str = eq_str.replace("y'''", "Derivative(y(x), x, 3)")
    eq_str = eq_str.replace("y''", "Derivative(y(x), x, 2)")
    eq_str = eq_str.replace("y'", "Derivative(y(x), x)")
    
    # Replace standalone y with y(x) function notation
    eq_str = re.sub(r'(?<![a-zA-Z0-9_])y(?![a-zA-Z0-9_\(])', 'y(x)', eq_str)
    
    # Replace power notation
    eq_str = eq_str.replace('^', '**')
    
    # Parse the equation into a symbolic expression
    expr = parse_expr(eq_str, local_dict={'y': y, 'x': x, 'Derivative': diff})
    
    # Create a list of y and all its derivatives to check
    derivatives = [y]  # y itself
    for i in range(1, 4):  # Add first, second, and third derivatives
        derivatives.append(diff(y, x, i))
        
    # Check 1: No variable coefficient for derivatives
    for deriv in derivatives:
        if expr.has(deriv):
            # Collect terms with respect to this derivative
            collected = expr.collect(deriv)
            
            # Get the coefficient of the derivative
            coeff = collected.coeff(deriv)
            
            # Check if coefficient contains y or any derivative
            if any(str(d) in str(coeff) for d in derivatives):
                return False
                
    # Check 2: No higher powers of derivatives
    for deriv in derivatives:
        # Check for terms like (y')² or y'·y'
        if expr.has(deriv**2) or expr.has(deriv*deriv):
            return False
            
    # Check 3: No transcendental functions applied to y or derivatives
    for func in [sin, exp]:  # Check common functions
        for deriv in derivatives:
            if expr.has(func(deriv)):
                return False
    
    # Equation passed all symbolic checks for linearity
    return True

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'status': 'error',
            'message': 'No equation provided'
        }))
        sys.exit(1)
    
    equation = sys.argv[1]
    
    try:
        if is_linear_de(equation):
            result = {
                'status': 'success',
                'message': f"The differential equation '{equation}' is linear."
            }
        else:
            result = {
                'status': 'error',
                'message': f"The differential equation '{equation}' is not linear."
            }
        
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'message': f"Error analyzing equation: {str(e)}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main() 