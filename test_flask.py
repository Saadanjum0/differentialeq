import unittest
import json
from app import app

class FlaskAppTestCase(unittest.TestCase):
    """Test case for the Flask application"""

    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        """Test that the home page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('version', data)
        self.assertIn('timestamp', data)

    def test_check_linearity(self):
        """Test the linearity checking endpoint"""
        response = self.app.post('/check_linearity', 
                                json={'equation': "y'' + 3*y' + 2*y = sin(x)"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('is_linear', data)
        self.assertTrue(data['is_linear'])

    def test_verify_solution(self):
        """Test the solution verification endpoint"""
        response = self.app.post('/verify_solution', 
                                json={
                                    'de': "y'' + y = 0",
                                    'solution': "sin(x)"
                                })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('is_solution', data)
        self.assertTrue(data['is_solution'])

    def test_invalid_equation(self):
        """Test handling of invalid equations"""
        response = self.app.post('/check_linearity', 
                                json={'equation': "invalid_equation"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()