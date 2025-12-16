# Load Testing

Performance testing framework for the onboarding chatbot measuring latency, throughput, and system bottlenecks under concurrent load.

## Quick Start

```bash
# One-command test + visualization (recommended)
src/onboarding_agent/loadtest/run_load_test.sh

# Or run manually
PYTHONPATH=src uv run python src/onboarding_agent/loadtest/run_load.py --queries "100"
PYTHONPATH=src uv run python src/onboarding_agent/loadtest/visualize_load_results.py
```

## Key Metrics

| Metric       | Description                   | Typical (qwen2.5:7b) |
| ------------ | ----------------------------- | -------------------- |
| Mean Latency | Average response time         | 12-18s               |
| P95 Latency  | 95th percentile response time | 15-25s               |
| Throughput   | Queries per second            | 0.1-0.3 q/s          |
| Success Rate | % queries completed           | >95%                 |

## Test Configuration

- **Query count**: 100 queries
- **Concurrency**: 10 workers (ThreadPoolExecutor)
- **Test data**: Reuses questions from `eval/questions.jsonl`
- **Architecture**: Synchronous (optimal for single Ollama instance)

## Example Output

```
================================================================================
DETAILED LOAD TEST REPORT
================================================================================

📊 TEST SUMMARY
   Total Queries: 100
   Successful: 98 (98.0%)
   Failed: 2

⚡ PERFORMANCE METRICS
Queries      Workers    Mean Lat     P95 Lat      Throughput      Success %
---------------------------------------------------------------------------
100          10         15.241       18.983       0.18            98.0

🔍 BOTTLENECK ANALYSIS
   Primary Bottleneck: LLM inference time (Ollama)
   Mean Latency: 15.241s per query
   → Dominated by model processing time

🚀 OPTIMIZATION RECOMMENDATIONS

1. [🔴 CRITICAL] Model Optimization
   Issue: Mean latency: 15.24s per query
   💡 Recommendation: Switch to faster model (qwen2.5:3b or llama3.2:3b)
   📈 Expected Impact: 60-80% latency reduction

2. [🟡 HIGH] Response Caching
   Issue: 100.0% of queries use expensive RAG
   💡 Recommendation: Implement semantic caching for RAG responses
   📈 Expected Impact: 30-50% faster for similar queries

3. [🟡 HIGH] Async/Parallel Processing
   Issue: Low throughput: 0.18 queries/sec
   💡 Recommendation: Enable async processing with multiple Ollama instances
   📈 Expected Impact: 2-3x throughput increase
```

Results saved to `src/onboarding_agent/loadtest/results/load_test_results.json` with detailed per-query metrics and failure analysis.

## Bottleneck Analysis

**Primary bottleneck**: LLM inference time (Ollama with qwen2.5:7b)  
**Secondary**: Sequential processing limits throughput  
**Scaling**: Latency grows 1.2-1.5x from 50→200 queries (moderate degradation)

## Optimization Recommendations

1. **🔴 Model optimization**: Use qwen2.5:3b → 60-80% faster
2. **🟡 Semantic caching**: Cache RAG responses → 30-50% improvement
3. **🟡 Async processing**: Multiple Ollama instances → 2-3x throughput
4. **⚪ RAG tuning**: Optimize vector search → 10-20% faster

## Custom Configuration

```bash
# Different query count
PYTHONPATH=src uv run python src/onboarding_agent/loadtest/run_load.py --queries "100" --workers 5

# Custom output location
PYTHONPATH=src uv run python src/onboarding_agent/loadtest/run_load.py --output my_test.json

# Different test questions
PYTHONPATH=src uv run python src/onboarding_agent/loadtest/run_load.py --questions-file path/to/questions.jsonl
```

## Files

- `run_load.py` - Load test framework with concurrent execution
- `visualize_load_results.py` - Results viewer with ASCII charts
- `run_load_test.sh` - Helper script (runs test + visualization)
- `results/` - Test results stored here
