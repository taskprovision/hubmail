#!/bin/bash
# Comprehensive test script for the HubMail Python application
# This script can run tests locally or in the Docker container

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DOCKER_MODE=false
SPECIFIC_TEST=""
VERBOSE=false
COVERAGE=false

# Function to display usage information
usage() {
    echo -e "${BLUE}Usage:${NC} $0 [options]"
    echo
    echo "Options:"
    echo "  -d, --docker       Run tests in Docker container"
    echo "  -t, --test NAME    Run specific test module (e.g., test_api)"
    echo "  -v, --verbose      Run tests in verbose mode"
    echo "  -c, --coverage     Run tests with coverage report"
    echo "  -h, --help         Display this help message"
    echo
    echo "Examples:"
    echo "  $0                         # Run all tests locally"
    echo "  $0 -d                      # Run all tests in Docker"
    echo "  $0 -t test_email_processor # Run only email processor tests"
    echo "  $0 -d -t test_api -c       # Run API tests in Docker with coverage"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--docker)
            DOCKER_MODE=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error:${NC} Unknown option $1"
            usage
            ;;
    esac
done

# Function to check if Docker container is running
check_docker_container() {
    if ! docker ps | grep -q email-app; then
        echo -e "${RED}Error:${NC} Docker container 'email-app' is not running."
        echo -e "Start the container with: ${YELLOW}docker-compose up -d${NC}"
        exit 1
    fi
}

# Function to run tests locally
run_local_tests() {
    echo -e "${BLUE}Running tests locally...${NC}"
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error:${NC} Python 3 is not installed or not in PATH."
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -d "tests" ]; then
        echo -e "${YELLOW}Warning:${NC} 'tests' directory not found in current directory."
        echo -e "Changing to python_app directory..."
        
        if [ -d "../python_app" ]; then
            cd ../python_app
        elif [ -d "python_app" ]; then
            cd python_app
        else
            echo -e "${RED}Error:${NC} Cannot find python_app directory."
            exit 1
        fi
    fi
    
    # Install test dependencies if needed
    echo -e "${BLUE}Checking test dependencies...${NC}"
    if [ -f "tests/requirements-test.txt" ]; then
        echo -e "${YELLOW}Installing test dependencies from requirements-test.txt...${NC}"
        python3 -m pip install -r tests/requirements-test.txt
    else
        echo -e "${YELLOW}requirements-test.txt not found. Installing basic test dependencies...${NC}"
        python3 -m pip install pytest pytest-asyncio pytest-cov fastapi pydantic httpx prefect python-dotenv
    fi
    
    # Prepare test command
    TEST_CMD="python3 -m pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=. --cov-report=term --cov-report=html"
    fi
    
    if [ -n "$SPECIFIC_TEST" ]; then
        # Check if the test file exists
        if [ -f "tests/${SPECIFIC_TEST}.py" ]; then
            TEST_CMD="$TEST_CMD tests/${SPECIFIC_TEST}.py"
        else
            echo -e "${RED}Error:${NC} Test file 'tests/${SPECIFIC_TEST}.py' not found."
            exit 1
        fi
    else
        TEST_CMD="$TEST_CMD tests/"
    fi
    
    # Run the tests
    echo -e "${BLUE}Running command:${NC} $TEST_CMD"
    eval $TEST_CMD
    
    # Check test result
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
    else
        echo -e "${RED}Some tests failed.${NC}"
        exit 1
    fi
    
    # Show coverage report location if generated
    if [ "$COVERAGE" = true ]; then
        echo -e "${BLUE}Coverage report generated in:${NC} htmlcov/index.html"
    fi
}

# Function to run tests in Docker
run_docker_tests() {
    echo -e "${BLUE}Running tests in Docker container...${NC}"
    
    # Check if Docker is running
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error:${NC} Docker is not installed or not in PATH."
        exit 1
    fi
    
    # Check if the container is running
    check_docker_container
    
    # Install test dependencies in the container
    echo -e "${BLUE}Installing test dependencies in Docker container...${NC}"
    if [ -f "tests/requirements-test.txt" ]; then
        docker cp tests/requirements-test.txt email-app:/app/tests/
        docker exec -it email-app pip install -r /app/tests/requirements-test.txt
    else
        docker exec -it email-app pip install pytest pytest-asyncio pytest-cov fastapi pydantic httpx prefect python-dotenv
    fi
    
    # Prepare test command
    TEST_CMD="python -m pytest"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=. --cov-report=term"
    fi
    
    if [ -n "$SPECIFIC_TEST" ]; then
        TEST_CMD="$TEST_CMD tests/${SPECIFIC_TEST}.py"
    else
        TEST_CMD="$TEST_CMD tests/"
    fi
    
    # Run the tests in Docker
    echo -e "${BLUE}Running command in Docker:${NC} $TEST_CMD"
    docker exec -it email-app bash -c "cd /app && $TEST_CMD"
    
    # Check test result
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
    else
        echo -e "${RED}Some tests failed.${NC}"
        exit 1
    fi
}

# Main execution
echo -e "${BLUE}=== HubMail Python App Test Runner ===${NC}"
echo -e "${BLUE}Mode:${NC} $([ "$DOCKER_MODE" = true ] && echo "Docker" || echo "Local")"
if [ -n "$SPECIFIC_TEST" ]; then
    echo -e "${BLUE}Test:${NC} $SPECIFIC_TEST"
else
    echo -e "${BLUE}Test:${NC} All tests"
fi
echo -e "${BLUE}Verbose:${NC} $([ "$VERBOSE" = true ] && echo "Yes" || echo "No")"
echo -e "${BLUE}Coverage:${NC} $([ "$COVERAGE" = true ] && echo "Yes" || echo "No")"
echo

# Run tests based on mode
if [ "$DOCKER_MODE" = true ]; then
    run_docker_tests
else
    run_local_tests
fi

echo -e "${BLUE}=== Test Run Complete ===${NC}"
