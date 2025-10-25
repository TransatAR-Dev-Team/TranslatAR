#!/usr/bin/env python3
"""
Test runner for Google OAuth backend tests
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests for the auth controller"""
    print("🧪 Running Google OAuth Backend Tests")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    print("-" * 30)
    unit_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_auth_controller.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(unit_result.stdout)
    if unit_result.stderr:
        print("STDERR:", unit_result.stderr)
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    print("-" * 30)
    integration_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_auth_integration.py", 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(integration_result.stdout)
    if integration_result.stderr:
        print("STDERR:", integration_result.stderr)
    
    # Run all tests together
    print("\nRunning All Tests...")
    print("-" * 30)
    all_tests_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", "--tb=short", "--cov=auth_controller", "--cov-report=term-missing"
    ], capture_output=True, text=True)
    
    print(all_tests_result.stdout)
    if all_tests_result.stderr:
        print("STDERR:", all_tests_result.stderr)
    
    # Summary
    print("\nTest Summary")
    print("=" * 50)
    print(f"Unit Tests: {'PASSED' if unit_result.returncode == 0 else 'FAILED'}")
    print(f"Integration Tests: {'PASSED' if integration_result.returncode == 0 else 'FAILED'}")
    print(f"All Tests: {'PASSED' if all_tests_result.returncode == 0 else 'FAILED'}")
    
    return all_tests_result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
