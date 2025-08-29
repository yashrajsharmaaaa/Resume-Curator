#!/usr/bin/env python3
"""
Test runner script for Resume Curator backend tests.

This script provides a convenient way to run tests with different configurations
and generate coverage reports for the SDE1 portfolio demonstration.
"""

import os
import sys
import subprocess
import argparse


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Resume Curator backend tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = "python -m pytest"
    
    # Add verbosity
    if args.verbose:
        pytest_cmd += " -v"
    else:
        pytest_cmd += " -q"
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd += " --cov=. --cov-report=term-missing --cov-report=html:htmlcov"
    
    # Skip slow tests if requested
    if args.fast:
        pytest_cmd += " -m 'not slow'"
    
    # Add specific test markers
    if args.unit:
        pytest_cmd += " -m unit"
    elif args.integration:
        pytest_cmd += " -m integration"
    elif args.api:
        pytest_cmd += " -m api"
    
    # Add test directory
    pytest_cmd += " tests/"
    
    print("🧪 Resume Curator Backend Test Runner")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"Pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest is not installed. Please install test dependencies:")
        print("pip install pytest pytest-asyncio pytest-cov")
        return 1
    
    # Run the tests
    success = run_command(pytest_cmd, "Backend Tests")
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("- Terminal: See output above")
            print("- HTML: Open htmlcov/index.html in your browser")
        
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())