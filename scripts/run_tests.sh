#!/bin/bash
# Test runner script for Goranov Barbershop

set -e  # Exit on error

echo "================================"
echo "Goranov Barbershop Test Runner"
echo "================================"
echo ""

# Check if pytest is installed
if ! python -c "import pytest" &> /dev/null; then
    echo "Error: pytest not installed. Installing test dependencies..."
    pip install -r requirements.txt
fi

# Parse command line arguments
MODE="${1:-all}"

case "$MODE" in
    "unit")
        echo "Running unit tests only..."
        pytest tests/ -m unit -v
        ;;
    "integration")
        echo "Running integration tests only..."
        pytest tests/ -m integration -v
        ;;
    "e2e")
        echo "Running E2E tests only..."
        pytest tests/ -m e2e -v
        ;;
    "concurrent")
        echo "Running concurrent tests only..."
        pytest tests/ -m concurrent -v
        ;;
    "coverage")
        echo "Running all tests with coverage report..."
        pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
        echo ""
        echo "Coverage HTML report generated in htmlcov/index.html"
        ;;
    "quick")
        echo "Running quick test suite (unit + concurrent)..."
        pytest tests/ -m "unit or concurrent" -v
        ;;
    "all")
        echo "Running all tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 {unit|integration|e2e|concurrent|coverage|quick|all}"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  e2e         - Run end-to-end tests only"
        echo "  concurrent  - Run concurrent booking tests only"
        echo "  coverage    - Run all tests with coverage report"
        echo "  quick       - Run quick test suite (unit + concurrent)"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "Tests complete!"
