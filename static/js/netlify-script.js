document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements for linearity checker
    const checkLinearityBtn = document.getElementById('check-linearity');
    const equationInput = document.getElementById('equation-input');
    const linearityResult = document.getElementById('linearity-result');
    
    // Get DOM elements for solution verifier
    const verifySolutionBtn = document.getElementById('verify-solution');
    const deInput = document.getElementById('de-input');
    const solutionInput = document.getElementById('solution-input');
    const verificationResult = document.getElementById('verification-result');
    const plotContainer = document.getElementById('plot-container');
    
    // Set up example buttons
    document.querySelectorAll('.use-example-btn').forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            const de = this.getAttribute('data-de');
            const solution = this.getAttribute('data-solution');
            
            // Select appropriate input fields based on target
            if (target === 'linearity' && de) {
                equationInput.value = de;
            } else if (target === 'solution') {
                if (de) deInput.value = de;
                if (solution) solutionInput.value = solution;
            }
            
            // Provide visual feedback
            this.classList.add('btn-active');
            setTimeout(() => {
                this.classList.remove('btn-active');
            }, 300);
        });
    });
    
    // Make inline code examples clickable
    document.querySelectorAll('.examples-mini code').forEach(codeElement => {
        codeElement.addEventListener('click', function() {
            const codeText = this.textContent;
            
            // Determine which section the code belongs to
            const parentSection = this.closest('section');
            
            if (parentSection.id === 'linearity-checker') {
                equationInput.value = codeText;
                // Optional: Trigger the check
                // checkLinearityBtn.click();
            } else if (parentSection.id === 'solution-verifier') {
                // For solution verifier, check if it's a DE or solution
                // This is a simple heuristic - DE examples typically contain y' while solutions contain y =
                if (codeText.includes('y\'') && !codeText.includes('y =')) {
                    deInput.value = codeText;
                } else if (codeText.includes('y =')) {
                    solutionInput.value = codeText;
                }
            }
            
            // Visual feedback
            this.style.backgroundColor = '#c6e3f7';
            setTimeout(() => {
                this.style.backgroundColor = '';
            }, 300);
        });
    });
    
    // Format equation helper
    function formatEquation(equation) {
        // Simple trim to clean up whitespace without altering the equation too much
        return equation.trim();
    }
    
    // Display results with appropriate styling
    function displayResult(element, message, isSuccess) {
        element.innerHTML = '';
        const resultClass = isSuccess ? 'success-message' : 'error-message';
        const resultElement = document.createElement('div');
        resultElement.className = resultClass;
        resultElement.textContent = message;
        element.appendChild(resultElement);
    }
    
    // Display a plot
    function displayPlot(plotUrl) {
        if (plotUrl) {
            plotContainer.innerHTML = '';
            const plotImage = document.createElement('img');
            plotImage.src = plotUrl;
            plotImage.alt = 'Solution plot';
            plotImage.className = 'solution-plot';
            plotContainer.appendChild(plotImage);
            // Make sure the plot is visible
            plotContainer.style.display = 'block';
        } else {
            plotContainer.innerHTML = '';
            plotContainer.style.display = 'none';
        }
    }
    
    // Check if a differential equation is linear
    checkLinearityBtn.addEventListener('click', function() {
        const equation = formatEquation(equationInput.value);
        
        if (!equation) {
            displayResult(linearityResult, 'Please enter a differential equation.', false);
            return;
        }
        
        // Show loading state
        linearityResult.innerHTML = '<div class="loading">Checking...</div>';
        
        // Create form data for the request
        const formData = new URLSearchParams();
        formData.append('equation', equation);
        
        // Make API request to Netlify function
        fetch('/.netlify/functions/check_linearity', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayResult(linearityResult, data.message, true);
            } else {
                displayResult(linearityResult, data.message, false);
            }
        })
        .catch(error => {
            displayResult(linearityResult, 'Error: ' + error.message, false);
        });
    });
    
    // Verify if a function is a solution to a differential equation
    verifySolutionBtn.addEventListener('click', function() {
        const de = formatEquation(deInput.value);
        const solution = formatEquation(solutionInput.value);
        
        if (!de || !solution) {
            displayResult(verificationResult, 'Please enter both the differential equation and the proposed solution.', false);
            return;
        }
        
        // Show loading state
        verificationResult.innerHTML = '<div class="loading">Verifying...</div>';
        plotContainer.innerHTML = '';
        
        // Create form data for the request
        const formData = new URLSearchParams();
        formData.append('de', de);
        formData.append('solution', solution);
        
        // Make API request to Netlify function
        fetch('/.netlify/functions/verify_solution', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("API Response:", data); // Debug output
            
            if (data.status === 'success') {
                displayResult(verificationResult, data.message, true);
            } else {
                displayResult(verificationResult, data.message, false);
            }
            
            // Display plot if available
            if (data.plot_url) {
                console.log("Plot URL:", data.plot_url); // Debug output
                displayPlot(data.plot_url);
            } else {
                plotContainer.style.display = 'none';
            }
        })
        .catch(error => {
            displayResult(verificationResult, 'Error: ' + error.message, false);
            plotContainer.style.display = 'none';
        });
    });
}); 