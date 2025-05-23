#!/usr/bin/env python3
"""
Test runner for the HubMail Python application.
"""
import unittest
import sys
import os
import asyncio

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_async_tests():
    """Run all tests, including async tests."""
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_async_tests()
    sys.exit(0 if success else 1)
