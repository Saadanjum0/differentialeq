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
    const de = params.get('de');
    const solution = params.get('solution');
    
    if (!de || !solution) {
      return {
        statusCode: 400,
        body: JSON.stringify({
          status: 'error',
          message: 'Please enter both the differential equation and the proposed solution.'
        })
      };
    }

    // Call Python script to verify solution
    const result = await runPythonScript(de, solution);
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

function runPythonScript(de, solution) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', ['solution_verifier.py', de, solution]);
    
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