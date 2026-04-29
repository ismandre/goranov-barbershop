#!/bin/bash
# Verification script for Phase 4 implementation

echo "========================================="
echo "Phase 4: Testing & Refinement"
echo "Implementation Verification"
echo "========================================="
echo ""

# Check test dependencies
echo "📦 Checking test dependencies..."
python -c "import pytest; import faker; import freezegun" 2>/dev/null && echo "✅ Test dependencies installed" || echo "❌ Missing test dependencies"

# Check logging module
echo "📝 Checking logging configuration..."
python -c "from app.logging_config import setup_logging, get_logger" 2>/dev/null && echo "✅ Logging module present" || echo "❌ Logging module missing"

# Check middleware
echo "🔧 Checking request ID middleware..."
python -c "from app.middleware.request_id import RequestIDMiddleware" 2>/dev/null && echo "✅ Middleware present" || echo "❌ Middleware missing"

# Check retry utility
echo "🔁 Checking retry utility..."
python -c "from app.utils.retry import retry" 2>/dev/null && echo "✅ Retry utility present" || echo "❌ Retry utility missing"

# Check test files
echo "🧪 Checking test files..."
test -f tests/conftest.py && echo "✅ conftest.py" || echo "❌ conftest.py missing"
test -f tests/test_concurrent_booking.py && echo "✅ test_concurrent_booking.py" || echo "❌ test_concurrent_booking.py missing"
test -f tests/test_appointment_service.py && echo "✅ test_appointment_service.py" || echo "❌ test_appointment_service.py missing"
test -f tests/test_webhook_e2e.py && echo "✅ test_webhook_e2e.py" || echo "❌ test_webhook_e2e.py missing"

# Check scripts
echo "📜 Checking scripts..."
test -x scripts/run_tests.sh && echo "✅ run_tests.sh (executable)" || echo "❌ run_tests.sh missing or not executable"
test -f scripts/add_indexes.py && echo "✅ add_indexes.py" || echo "❌ add_indexes.py missing"

# Check documentation
echo "📚 Checking documentation..."
test -f CONCURRENCY_NOTE.md && echo "✅ CONCURRENCY_NOTE.md" || echo "❌ CONCURRENCY_NOTE.md missing"
test -f PHASE4_IMPLEMENTATION_SUMMARY.md && echo "✅ PHASE4_IMPLEMENTATION_SUMMARY.md" || echo "❌ PHASE4_IMPLEMENTATION_SUMMARY.md missing"

echo ""
echo "========================================="
echo "🧪 Running Critical Tests"
echo "========================================="
echo ""

# Run concurrent booking tests
echo "Testing concurrent booking prevention..."
python -m pytest tests/test_concurrent_booking.py -v -m concurrent --tb=line 2>&1 | grep -E "(PASSED|FAILED|test_concurrent)" || echo "Tests not run"

echo ""
echo "========================================="
echo "📊 Test Coverage Report"
echo "========================================="
echo ""

# Run coverage
python -m pytest tests/test_appointment_service.py tests/test_concurrent_booking.py --cov=app.services.appointment_service --cov-report=term-missing --tb=no -q 2>&1 | tail -20

echo ""
echo "========================================="
echo "✅ Verification Complete"
echo "========================================="
echo ""
echo "For full test suite: ./scripts/run_tests.sh"
echo "For coverage report: ./scripts/run_tests.sh coverage"
echo "For logs: tail -f logs/app.log"
