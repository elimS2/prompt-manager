# Contributing to Prompt Manager

First off, thank you for considering contributing to Prompt Manager! It's people like you that make Prompt Manager such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the style guidelines
6. Issue that pull request!

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv, virtualenv, etc.)

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/prompt-manager.git
   cd prompt-manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. **Set up the database**
   ```bash
   make init-db seed-db
   ```

5. **Run the tests to ensure everything is working**
   ```bash
   make test
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write your code
- Add or update tests
- Update documentation if needed

### 3. Run Quality Checks
```bash
# Format your code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run all tests
make test

# Or run all checks at once
make check
```

### 4. Commit Your Changes
Write clear, concise commit messages:
```bash
git add .
git commit -m "Add feature: brief description of changes"
```

Commit message guidelines:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### 5. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request
Go to the repository on GitHub and create a pull request from your fork.

## Style Guidelines

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

### Code Style

```python
# Good
def calculate_total(items: List[Item]) -> float:
    """Calculate the total price of items.
    
    Args:
        items: List of Item objects
        
    Returns:
        Total price as float
    """
    return sum(item.price for item in items)

# Bad
def calc(i):
    return sum([x.price for x in i])
```

### Type Hints

Always use type hints for function arguments and return values:
```python
from typing import List, Dict, Optional

def process_data(data: Dict[str, Any]) -> Optional[str]:
    ...
```

### Docstrings

Use Google-style docstrings:
```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
```

### Testing

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

```python
def test_prompt_creation_with_valid_data(db_session):
    """Test that a prompt can be created with valid data."""
    # Arrange
    data = {
        'title': 'Test Prompt',
        'content': 'Test content'
    }
    
    # Act
    service = PromptService()
    prompt = service.create_prompt(data)
    
    # Assert
    assert prompt.title == 'Test Prompt'
    assert prompt.content == 'Test content'
```

## Project Structure

When adding new features, follow the existing structure:

```
app/
├── models/        # Domain models
├── repositories/  # Data access layer
├── services/      # Business logic
├── controllers/   # HTTP handlers
├── templates/     # HTML templates
└── static/        # CSS, JS, images

tests/
├── unit/         # Unit tests
└── integration/  # Integration tests
```

## Documentation

- Update the README.md if you change functionality
- Add docstrings to all public functions and classes
- Update API.md if you change API endpoints
- Include examples where appropriate

## Review Process

### What We Look For

- **Code quality**: Is the code clean, readable, and maintainable?
- **Testing**: Are there adequate tests? Do they pass?
- **Documentation**: Is the feature/change documented?
- **Style**: Does the code follow our style guidelines?
- **Design**: Does the change fit well with the existing architecture?

### Review Timeline

We aim to review pull requests within 2-3 days. If you haven't heard back in a week, feel free to ping us.

## Recognition

Contributors who submit accepted pull requests will be added to our contributors list in the README.

## Questions?

Feel free to open an issue with your question or reach out to the maintainers directly.

Thank you for contributing! 🎉