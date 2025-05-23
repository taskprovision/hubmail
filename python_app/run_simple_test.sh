#!/bin/bash
# Simple test script for the HubMail Python application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== HubMail Python App Simple Test ===${NC}"

# Install required dependencies
echo -e "${YELLOW}Installing required dependencies...${NC}"
pip install pytest pytest-asyncio fastapi pydantic httpx prefect python-dotenv

# Create a simple test file
echo -e "${YELLOW}Creating a simple test file...${NC}"
mkdir -p tests

cat > tests/test_simple.py << 'EOF'
import unittest
import sys
import os

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSimple(unittest.TestCase):
    """Simple test case to verify the testing environment."""

    def test_import_modules(self):
        """Test that we can import required modules."""
        try:
            import pytest
            import fastapi
            import pydantic
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import required modules: {str(e)}")

    def test_environment(self):
        """Test that the environment is set up correctly."""
        self.assertEqual(1 + 1, 2, "Basic assertion works")

if __name__ == '__main__':
    unittest.main()
EOF

# Run the test
echo -e "${YELLOW}Running the test...${NC}"
python -m unittest tests/test_simple.py

# Check the result
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Simple test passed! The testing environment is working.${NC}"
    echo -e "${BLUE}You can now create more complex tests for the application.${NC}"
else
    echo -e "${RED}Test failed. Please check the error messages above.${NC}"
fi
