# Contributing to Differential Equation Analyzer

Thank you for your interest in contributing to the Differential Equation Analyzer! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/differential-equation-app.git
   cd differential-equation-app
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request from your fork to our main repository

## Code Style Guidelines

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex algorithms or mathematical operations
- Keep functions focused and single-purpose
- Use type hints where appropriate

## Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Run tests using:
  ```bash
  python -m unittest discover tests
  ```

## Documentation

- Update README.md if you add new features
- Document API changes in the API documentation
- Include docstrings for new functions and classes
- Add comments explaining complex mathematical operations

## Mathematical Guidelines

When implementing differential equation related features:

1. **Linearity Checking**
   - Clearly document the criteria used
   - Handle edge cases appropriately
   - Provide mathematical justification

2. **Solution Verification**
   - Include error tolerance parameters
   - Document numerical methods used
   - Handle special cases (e.g., singular points)

3. **Plotting**
   - Use appropriate scales
   - Label axes clearly
   - Include grid lines where helpful
   - Handle domain/range appropriately

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the requirements.txt if you add dependencies
3. The PR will be merged once you have the sign-off of at least one maintainer

## Code Review Criteria

Your contribution will be reviewed for:

- Code quality and style
- Test coverage
- Documentation completeness
- Mathematical correctness
- Performance considerations

## Questions or Problems?

- Open an issue for bugs
- Use discussions for general questions
- Tag maintainers for urgent issues

Thank you for contributing! 