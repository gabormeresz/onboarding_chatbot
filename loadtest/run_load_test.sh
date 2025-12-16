#!/bin/bash
# Quick helper to run load test and visualize results

echo "=========================================="
echo "Running Load Test (100 queries)"
echo "=========================================="
echo ""

# Get the project root (2 levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Set PYTHONPATH to include src directory
export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH}"

# Run load test
uv run python loadtest/run_load.py --queries "100" --workers 10

# Check if test was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Generating Visual Report"
    echo "=========================================="
    echo ""
    
    # Generate visualization
    uv run python loadtest/visualize_load_results.py
    
    echo ""
    echo "✅ Load test complete!"
    echo "Results saved to: loadtest/results/load_test_results.json"
else
    echo ""
    echo "❌ Load test failed. Check the output above for errors."
    exit 1
fi
