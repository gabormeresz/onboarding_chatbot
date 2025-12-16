# Evaluation Framework

Automated testing for the agentic RAG chatbot measuring routing accuracy, escalation correctness, and performance.

## Quick Start

```bash
# Basic evaluation (~1 minute)
PYTHONPATH=src uv run python src/onboarding_agent/eval/run_eval.py

# With LLM-as-judge quality metrics (complete, slower)
PYTHONPATH=src uv run python src/onboarding_agent/eval/run_eval.py --use-llm-judges

# Visualize results
uv run python src/onboarding_agent/eval/visualize_results.py src/onboarding_agent/eval/results/eval_results.json
```

## Key Metrics

| Metric               | Description                      | Target |
| -------------------- | -------------------------------- | ------ |
| Overall Accuracy     | Routing & escalation correctness | ≥85%   |
| F1 Score             | Precision/recall balance         | ≥65%   |
| Response Gen Cases   | Standard query success rate      | 100%   |
| Escalation Detection | Critical issue identification    | ≥50%   |
| Avg Latency          | Response time per query          | <6s    |

## Test Dataset

18 test cases across 3 categories:

- **Standard queries (IDs 1-10)**: RAG-answerable questions (HR, equipment, onboarding)
- **Edge cases (IDs 11-14)**: Ambiguous scenarios requiring judgment
- **Critical escalations (IDs 15-18)**: Security incidents, urgent issues (must escalate)

Format:

```json
{
  "id": 1,
  "question": "How many home office days per week?",
  "expected": {
    "route": "response_generation",
    "escalation": false
  }
}
```

## Metrics Explained

**Overall Accuracy**: Correct routing (RAG vs escalation) AND escalation behavior  
**F1 Score**: Harmonic mean of precision and recall for escalation decisions  
**Response Gen Cases**: Success rate on standard RAG-answerable questions  
**Escalation Detection**: Success rate identifying critical issues requiring human intervention  
**Latency**: Average, min, max, and percentiles (P50/P90/P95/P99) tracked

Optional LLM-as-judge: Answer relevance and completeness (percentage scores)

## Example Output

```
================================================================================
DETAILED EVALUATION REPORT
================================================================================

📊 OVERALL RESULTS
   Total Tests: 18
   Passed: 16 (88.9%)
   Failed: 2

🎯 ROUTING METRICS
   Overall Accuracy:        88.9%
   F1 Score:                66.7%
   Response Gen Cases:     100.0%
   Escalation Detection:    50.0%

⚡ PERFORMANCE
   Average Latency: 5.590s
   Min Latency:     0.961s
   Max Latency:     8.256s

✨ QUALITY METRICS (LLM-Judged)
   Answer Relevance:        91.1%
   Answer Completeness:     72.8%

⏱️  LATENCY DISTRIBUTION
   P50 (median): 5.810s
   P90:          7.884s
   P95:          8.125s
   P99:          8.230s
```

Results saved to `results/eval_results.json` with detailed per-test data, failed test analysis, and slowest queries.

## Files

- `evaluate_graph.py` - Core evaluation framework (GraphEvaluator class)
- `run_eval.py` - CLI script
- `questions.jsonl` - 18 test cases
- `visualize_results.py` - Results viewer
- `demo_eval.py` - Quick 2-case demo

## Extensibility

Easy to add:

- RAG retrieval quality (e.g., context relevance)
- Token usage tracking
- Multi-turn conversation evaluation
- A/B testing between models
- Benchmark comparison with baseline
