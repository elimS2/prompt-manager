"""
Script to run tests with different configurations.
"""
import os
import sys
import subprocess


def run_command(command):
    """Run a command and return exit code."""
    print(f"\nRunning: {command}")
    print("-" * 60)
    return subprocess.call(command, shell=True)


def main():
    """Main function to run tests."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "all"
    
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Activate virtual environment if it exists
    venv_activate = os.path.join(project_root, "venv", "Scripts", "activate")
    if os.path.exists(venv_activate):
        print("Virtual environment found")
    
    exit_code = 0
    
    if test_type == "unit":
        print("Running unit tests...")
        exit_code = run_command("pytest tests/unit -v")
    
    elif test_type == "integration":
        print("Running integration tests...")
        exit_code = run_command("pytest tests/integration -v")
    
    elif test_type == "coverage":
        print("Running tests with coverage...")
        exit_code = run_command("pytest --cov=app --cov-report=html --cov-report=term")
        if exit_code == 0:
            print("\nCoverage report generated in htmlcov/index.html")
    
    elif test_type == "lint":
        print("Running linters...")
        commands = [
            "flake8 app tests --max-line-length=100 --ignore=E501,W503",
            "black --check app tests",
            "mypy app --ignore-missing-imports"
        ]
        for cmd in commands:
            code = run_command(cmd)
            if code != 0:
                exit_code = code
    
    elif test_type == "all":
        print("Running all tests...")
        exit_code = run_command("pytest -v")
    
    else:
        print(f"Unknown test type: {test_type}")
        print("Usage: python scripts/run_tests.py [unit|integration|coverage|lint|all]")
        exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())