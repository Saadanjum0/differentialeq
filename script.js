document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const checkLinearityBtn = document.getElementById('check-linearity-btn');
    const equationInput = document.getElementById('equation-input');
    const linearityResult = document.getElementById('linearity-result');
    
    const verifyBtn = document.getElementById('verify-solution-btn');
    const deInput = document.getElementById('de-input');
    const solutionInput = document.getElementById('solution-input');
    const verificationResult = document.getElementById('verification-result');
    
    const exampleBtns = document.querySelectorAll('.example-btn');
    
    // Add event listeners
    checkLinearityBtn.addEventListener('click', checkLinearity);
    verifyBtn.addEventListener('click', verifySolution);
    
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const equation = this.getAttribute('data-equation');
            const solution = this.getAttribute('data-solution');
            
            if (equation) {
                deInput.value = equation;
                equationInput.value = equation;
            }
            
            if (solution) {
                solutionInput.value = solution;
            }
        });
    });
    
    // Function to check if a differential equation is linear
    function checkLinearity() {
        const equation = equationInput.value.trim();
        
        if (!equation) {
            showResult(linearityResult, 'Please enter a differential equation.', 'error');
            return;
        }
        
        // Normalize the equation for analysis
        const normalizedEq = normalizeEquation(equation);
        
        // Check for nonlinear terms
        const isLinear = isLinearDE(normalizedEq);
        
        if (isLinear) {
            showResult(linearityResult, `The differential equation "${equation}" is linear.`, 'success');
        } else {
            showResult(linearityResult, `The differential equation "${equation}" is non-linear.`, 'error');
        }
    }
    
    // Function to verify if a function is a solution to a differential equation
    function verifySolution() {
        const de = deInput.value.trim();
        const solution = solutionInput.value.trim();
        
        if (!de || !solution) {
            showResult(verificationResult, 'Please enter both the differential equation and the proposed solution.', 'error');
            return;
        }
        
        // For this demo, we'll implement a simplified verification for some common cases
        const result = verifySimpleSolution(de, solution);
        
        if (result.isValid) {
            showResult(verificationResult, `The function "${solution}" is a solution to the differential equation "${de}".`, 'success');
        } else {
            showResult(verificationResult, `The function "${solution}" is NOT a solution to the differential equation "${de}". ${result.reason}`, 'error');
        }
    }
    
    // Helper function to display results
    function showResult(element, message, type) {
        element.innerHTML = `<p>${message}</p>`;
        element.className = 'result ' + type;
        
        // Render math expressions if needed
        if (window.MathJax) {
            MathJax.typeset();
        }
    }
    
    // Function to normalize the equation for analysis
    function normalizeEquation(equation) {
        // Remove spaces
        let normalized = equation.replace(/\s+/g, '');
        
        // Replace y', y'', etc. with standard notation
        normalized = normalized.replace(/y'/g, "y'");
        normalized = normalized.replace(/y''/g, "y''");
        
        return normalized;
    }
    
    // Function to check if a differential equation is linear
    function isLinearDE(equation) {
        // Check for nonlinear terms like y^2, sin(y), e^y, etc.
        const nonlinearPatterns = [
            /y\^[0-9]+/,        // y raised to a power (y^2, y^3, etc.)
            /y\*y/,             // y multiplied by y
            /sin\(.*y.*\)/,     // sin(y) or sin containing y
            /cos\(.*y.*\)/,     // cos(y) or cos containing y
            /tan\(.*y.*\)/,     // tan(y) or tan containing y
            /e\^.*y.*/,         // e^y or e^ containing y
            /ln\(.*y.*\)/,      // ln(y) or ln containing y
            /log\(.*y.*\)/,     // log(y) or log containing y
            /y.*\*.*y'/,        // y multiplied by y'
            /y'.*\*.*y/,        // y' multiplied by y
            /y'.*\*.*y'/,       // y' multiplied by y'
            /y'.*\^[0-9]+/      // y' raised to a power
        ];
        
        // Check if any nonlinear pattern is found
        for (const pattern of nonlinearPatterns) {
            if (pattern.test(equation)) {
                return false;
            }
        }
        
        return true;
    }
    
    // Function to verify if a function is a solution to a differential equation
    function verifySimpleSolution(de, solution) {
        // This is a simplified verification for demonstration purposes
        // In a real application, you would need to use a symbolic math library
        
        // Some predefined cases for demonstration
        const knownCases = [
            {
                de: "y' + y = 0",
                solution: "y = C*e^(-x)",
                isValid: true
            },
            {
                de: "y' + y = 0",
                solution: "y = e^(-x)",
                isValid: true
            },
            {
                de: "y' + y = 0",
                solution: "y = e^x",
                isValid: false,
                reason: "Substituting y = e^x gives e^x + e^x = 2e^x ≠ 0"
            },
            {
                de: "y'' + y = 0",
                solution: "y = sin(x)",
                isValid: true
            },
            {
                de: "y'' + y = 0",
                solution: "y = cos(x)",
                isValid: true
            },
            {
                de: "y'' + y = 0",
                solution: "y = A*sin(x) + B*cos(x)",
                isValid: true
            },
            {
                de: "y'' + y = 0",
                solution: "y = e^x",
                isValid: false,
                reason: "Substituting y = e^x gives e^x + e^x = 2e^x ≠ 0"
            },
            {
                de: "y' = y^2 + x",
                solution: "y = tan(x)",
                isValid: false,
                reason: "This is a Riccati equation and tan(x) is not a solution."
            },
            {
                de: "y'' - 4y' + 4y = 0",
                solution: "y = (C1 + C2x)e^(2x)",
                isValid: true
            },
            {
                de: "y'' - 4y' + 4y = 0",
                solution: "y = C1*e^(2x) + C2*x*e^(2x)",
                isValid: true
            },
            {
                de: "y' + 2y = e^x",
                solution: "y = (1/3)e^x + Ce^(-2x)",
                isValid: true
            }
        ];
        
        // Normalize inputs for comparison
        const normalizedDE = normalizeEquation(de);
        const normalizedSolution = solution.replace(/\s+/g, '');
        
        // Look for a match in known cases
        for (const testCase of knownCases) {
            const testDE = normalizeEquation(testCase.de);
            const testSolution = testCase.solution.replace(/\s+/g, '');
            
            if (testDE === normalizedDE && 
                (testSolution === normalizedSolution || 
                 isEquivalentSolution(testSolution, normalizedSolution))) {
                return {
                    isValid: testCase.isValid,
                    reason: testCase.reason || ''
                };
            }
        }
        
        // If no match found
        return {
            isValid: false,
            reason: "Cannot verify this solution. Please try one of the example cases."
        };
    }
    
    // Function to check if two solutions are mathematically equivalent
    function isEquivalentSolution(sol1, sol2) {
        // This is a simplified check for demonstration
        // In a real application, you would need a symbolic math library
        
        // Check for common equivalences
        const equivalentPairs = [
            ["sin(x)", "A*sin(x)"],
            ["cos(x)", "B*cos(x)"],
            ["e^(-x)", "C*e^(-x)"],
            ["e^(2x)", "C1*e^(2x)"],
            ["x*e^(2x)", "C2*x*e^(2x)"]
        ];
        
        for (const [expr1, expr2] of equivalentPairs) {
            if ((sol1.includes(expr1) && sol2.includes(expr2)) || 
                (sol1.includes(expr2) && sol2.includes(expr1))) {
                return true;
            }
        }
        
        return false;
    }
}); 