const { spawn } = require('child_process');

exports.handler = async function(event, context) {
  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ status: 'error', message: 'Method Not Allowed' })
    };
  }

  try {
    // Parse the request body
    const params = new URLSearchParams(event.body);
    const equation = params.get('equation');
    
    if (!equation) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          status: 'error',
          message: 'Please enter a differential equation.'
        })
      };
    }

    // Call Python script to check linearity
    const result = await runPythonScript(equation);
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: result
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        status: 'error',
        message: 'Internal server error: ' + error.message
      })
    };
  }
};

function runPythonScript(equation) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', ['linearity_checker.py', equation]);
    
    let dataString = '';
    
    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      console.error(`Python stderr: ${data}`);
    });
    
    python.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(`Python process exited with code ${code}`));
      }
      resolve(dataString);
    });
  });
} 