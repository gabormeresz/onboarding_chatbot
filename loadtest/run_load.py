"""
Load testing script for the onboarding chatbot.

Tests the system with 50-200 concurrent queries to identify:
- Latency metrics (min, max, mean, p50, p95, p99)
- Bottlenecks in the system
- Performance optimization opportunities
"""

import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
from pathlib import Path
import argparse

from onboarding_agent.agent.graph import build_graph
from onboarding_agent.agent.state import build_initial_state


def load_test_questions(questions_file: str) -> List[Dict[str, Any]]:
    """Load questions from JSONL file."""
    questions = []
    with open(questions_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


def execute_single_query(graph, question: str, query_id: int) -> Dict[str, Any]:
    """
    Execute a single query and measure timing.

    Returns:
        Dict with timing information and result
    """
    start_time = time.time()

    try:
        initial_state = build_initial_state(question)
        result = graph.invoke(initial_state)

        end_time = time.time()
        latency = end_time - start_time

        return {
            "query_id": query_id,
            "question": question,
            "latency": latency,
            "success": True,
            "answer": result.get("answer", "No answer"),
            "intent": result.get("intent", "unknown"),
            "route_decision": result.get("route_decision", "unknown"),
            "error": None,
        }
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time

        return {
            "query_id": query_id,
            "question": question,
            "latency": latency,
            "success": False,
            "answer": None,
            "intent": None,
            "route_decision": None,
            "error": str(e),
        }


def run_load_test(
    num_queries: int,
    max_workers: int,
    questions_file: str = "eval/questions.jsonl",
) -> Dict[str, Any]:
    """
    Run load test with specified number of queries.

    Args:
        num_queries: Total number of queries to execute
        max_workers: Number of concurrent threads
        questions_file: Path to questions file

    Returns:
        Dictionary with test results and metrics
    """
    print(f"\n{'='*60}")
    print(f"Load Test: {num_queries} queries with {max_workers} workers")
    print(f"{'='*60}\n")

    # Load questions
    questions_data = load_test_questions(questions_file)

    # Build graph once (reuse across threads)
    print("Building graph...")
    graph = build_graph()

    # Prepare queries (cycle through questions if needed)
    queries = []
    for i in range(num_queries):
        q = questions_data[i % len(questions_data)]
        queries.append((i, q["question"]))

    # Execute queries concurrently
    print(f"Executing {num_queries} queries with {max_workers} concurrent workers...")

    test_start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(execute_single_query, graph, question, query_id)
            for query_id, question in queries
        ]

        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1

            # Progress indicator
            if completed % 10 == 0 or completed == num_queries:
                print(f"  Completed: {completed}/{num_queries}")

    test_end_time = time.time()
    total_duration = test_end_time - test_start_time

    # Calculate metrics
    metrics = calculate_metrics(results, total_duration)

    return {
        "num_queries": num_queries,
        "max_workers": max_workers,
        "results": results,
        "metrics": metrics,
    }


def calculate_metrics(
    results: List[Dict[str, Any]], total_duration: float
) -> Dict[str, Any]:
    """Calculate performance metrics from results."""

    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]

    latencies = [r["latency"] for r in successful_results]

    if not latencies:
        return {
            "error": "No successful queries",
            "total_queries": len(results),
            "failures": len(failed_results),
        }

    # Sort latencies for percentile calculation
    sorted_latencies = sorted(latencies)

    def percentile(data, p):
        """Calculate percentile."""
        k = (len(data) - 1) * (p / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(data) else f
        return data[f] + (k - f) * (data[c] - data[f])

    metrics = {
        "total_queries": len(results),
        "successful_queries": len(successful_results),
        "failed_queries": len(failed_results),
        "success_rate": len(successful_results) / len(results) * 100,
        # Latency metrics (in seconds)
        "latency": {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "p50": percentile(sorted_latencies, 50),
            "p95": percentile(sorted_latencies, 95),
            "p99": percentile(sorted_latencies, 99),
            "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        },
        # Throughput
        "throughput": {
            "total_duration": total_duration,
            "queries_per_second": len(successful_results) / total_duration,
        },
        # Route distribution
        "route_distribution": {},
    }

    # Calculate route distribution
    for result in successful_results:
        route = result.get("route_decision", "unknown")
        metrics["route_distribution"][route] = (
            metrics["route_distribution"].get(route, 0) + 1
        )

    return metrics


def print_metrics_report(test_result: Dict[str, Any]):
    """Print formatted metrics report."""
    metrics = test_result["metrics"]

    print(f"\n{'='*60}")
    print("LOAD TEST RESULTS")
    print(f"{'='*60}\n")

    print(f"Test Configuration:")
    print(f"  Total Queries: {test_result['num_queries']}")
    print(f"  Concurrent Workers: {test_result['max_workers']}")
    print(f"  Success Rate: {metrics['success_rate']:.2f}%")
    print(f"  Failed Queries: {metrics['failed_queries']}")

    print(f"\nLatency Metrics (seconds):")
    lat = metrics["latency"]
    print(f"  Min:      {lat['min']:.3f}s")
    print(f"  Max:      {lat['max']:.3f}s")
    print(f"  Mean:     {lat['mean']:.3f}s")
    print(f"  Median:   {lat['median']:.3f}s")
    print(f"  P95:      {lat['p95']:.3f}s")
    print(f"  P99:      {lat['p99']:.3f}s")
    print(f"  StdDev:   {lat['stdev']:.3f}s")

    print(f"\nThroughput:")
    print(f"  Total Duration: {metrics['throughput']['total_duration']:.2f}s")
    print(f"  Queries/sec:    {metrics['throughput']['queries_per_second']:.2f}")

    print(f"\nRoute Distribution:")
    for route, count in sorted(metrics["route_distribution"].items()):
        percentage = (count / metrics["successful_queries"]) * 100
        print(f"  {route}: {count} ({percentage:.1f}%)")


def identify_bottlenecks(all_test_results: List[Dict[str, Any]]):
    """
    Identify system bottlenecks from multiple test runs.
    """
    print(f"\n{'='*60}")
    print("BOTTLENECK ANALYSIS")
    print(f"{'='*60}\n")

    # Analyze latency growth as load increases
    print("Latency Growth Analysis:")
    print(
        f"{'Queries':<10} {'Mean Latency':<15} {'P95 Latency':<15} {'Throughput':<15}"
    )
    print("-" * 60)

    latency_growth = []
    for result in all_test_results:
        num_queries = result["num_queries"]
        metrics = result["metrics"]
        mean_lat = metrics["latency"]["mean"]
        p95_lat = metrics["latency"]["p95"]
        throughput = metrics["throughput"]["queries_per_second"]

        print(
            f"{num_queries:<10} {mean_lat:<15.3f} {p95_lat:<15.3f} {throughput:<15.2f}"
        )
        latency_growth.append((num_queries, mean_lat, p95_lat))

    # Identify bottlenecks
    print("\nIdentified Bottlenecks:")

    # Check if latency grows significantly
    if len(latency_growth) >= 2:
        first_mean = latency_growth[0][1]
        last_mean = latency_growth[-1][1]
        growth_factor = last_mean / first_mean

        if growth_factor > 1.5:
            print(f"  ⚠️  HIGH LATENCY GROWTH: {growth_factor:.2f}x increase")
            print(f"      Mean latency grew from {first_mean:.3f}s to {last_mean:.3f}s")
            print(f"      → Main Bottleneck: LLM inference (Ollama)")
        else:
            print(f"  ✓  Latency scales reasonably: {growth_factor:.2f}x growth")

    # Check absolute latency
    max_mean = max(result["metrics"]["latency"]["mean"] for result in all_test_results)
    if max_mean > 5.0:
        print(f"  ⚠️  HIGH ABSOLUTE LATENCY: {max_mean:.3f}s mean")
        print(f"      → Bottleneck: Model inference time")

    # Check throughput
    max_throughput = max(
        result["metrics"]["throughput"]["queries_per_second"]
        for result in all_test_results
    )
    if max_throughput < 2.0:
        print(f"  ⚠️  LOW THROUGHPUT: {max_throughput:.2f} queries/sec")
        print(f"      → Bottleneck: Sequential LLM processing")


def provide_optimization_recommendations(all_test_results: List[Dict[str, Any]]):
    """
    Provide concrete optimization recommendations based on test results.
    """
    print(f"\n{'='*60}")
    print("OPTIMIZATION RECOMMENDATIONS")
    print(f"{'='*60}\n")

    # Get metrics from the largest test
    largest_test = max(all_test_results, key=lambda x: x["num_queries"])
    metrics = largest_test["metrics"]

    recommendations = []

    # Recommendation 1: Model optimization
    mean_latency = metrics["latency"]["mean"]
    if mean_latency > 3.0:
        recommendations.append(
            {
                "priority": "HIGH",
                "category": "Model Optimization",
                "issue": f"High mean latency: {mean_latency:.2f}s per query",
                "recommendation": "Switch to a faster model (e.g., qwen2.5:3b or llama3.2:3b)",
                "expected_improvement": "40-60% latency reduction",
                "implementation": [
                    "Update models/config.py to use qwen2.5:3b-instruct",
                    "Test accuracy vs speed tradeoff",
                    "Consider caching frequent queries",
                ],
            }
        )

    # Recommendation 2: Caching
    route_dist = metrics.get("route_distribution", {})
    rag_percentage = (
        route_dist.get("needs_rag", 0) / metrics["successful_queries"] * 100
    )
    if rag_percentage > 30:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "Response Caching",
                "issue": f"{rag_percentage:.1f}% of queries use RAG (expensive)",
                "recommendation": "Implement semantic caching for RAG responses",
                "expected_improvement": "30-50% faster for repeated similar queries",
                "implementation": [
                    "Use LangChain's semantic cache with ChromaDB",
                    "Cache RAG results based on query embedding similarity",
                    "Set TTL of 1 hour for cache entries",
                ],
            }
        )

    # Recommendation 3: Parallel processing
    throughput = metrics["throughput"]["queries_per_second"]
    if throughput < 3.0:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "Parallel Processing",
                "issue": f"Low throughput: {throughput:.2f} queries/sec",
                "recommendation": "Add async support with multiple Ollama instances",
                "expected_improvement": "2-3x throughput increase",
                "implementation": [
                    "Set up Ollama with OLLAMA_NUM_PARALLEL=4",
                    "Convert graph.invoke() to graph.ainvoke()",
                    "Use asyncio for concurrent request handling",
                ],
            }
        )

    # Recommendation 4: RAG optimization
    recommendations.append(
        {
            "priority": "LOW",
            "category": "RAG Optimization",
            "issue": "Vector search can be optimized",
            "recommendation": "Optimize ChromaDB indexing and retrieval",
            "expected_improvement": "10-20% faster RAG queries",
            "implementation": [
                "Use HNSW index for faster similarity search",
                "Reduce default k (number of retrieved docs) from 4 to 3",
                "Pre-filter documents by metadata before vector search",
            ],
        }
    )

    # Print recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority']}] {rec['category']}")
        print(f"   Issue: {rec['issue']}")
        print(f"   Recommendation: {rec['recommendation']}")
        print(f"   Expected Improvement: {rec['expected_improvement']}")
        print(f"   Implementation:")
        for step in rec["implementation"]:
            print(f"     • {step}")
        print()


def save_results(all_test_results: List[Dict[str, Any]], output_file: str):
    """Save detailed results to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare simplified results (exclude full answer text)
    simplified_results = []
    for test_result in all_test_results:
        simplified = {
            "num_queries": test_result["num_queries"],
            "max_workers": test_result["max_workers"],
            "metrics": test_result["metrics"],
            "sample_failures": [
                {
                    "query_id": r["query_id"],
                    "question": r["question"],
                    "error": r["error"],
                }
                for r in test_result["results"]
                if not r["success"]
            ][
                :5
            ],  # Only keep first 5 failures
        }
        simplified_results.append(simplified)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(simplified_results, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed results saved to: {output_file}")


def main():
    """Main entry point for load testing."""
    parser = argparse.ArgumentParser(description="Load test the onboarding chatbot")
    parser.add_argument(
        "--queries",
        type=str,
        default="100",
        help="Comma-separated list of query counts to test (default: 100)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="loadtest/results/load_test_results.json",
        help="Output file for results",
    )
    parser.add_argument(
        "--questions-file",
        type=str,
        default="eval/questions.jsonl",
        help="Path to questions file",
    )

    args = parser.parse_args()

    # Parse query counts
    query_counts = [int(q.strip()) for q in args.queries.split(",")]

    print("=" * 60)
    print("ONBOARDING CHATBOT - LOAD TEST")
    print("=" * 60)
    print(f"\nTest Plan:")
    print(f"  Query Counts: {query_counts}")
    print(f"  Concurrent Workers: {args.workers}")
    print(f"  Questions File: {args.questions_file}")
    print(f"  Output File: {args.output}")

    # Run tests for each query count
    all_test_results = []

    for num_queries in query_counts:
        test_result = run_load_test(
            num_queries=num_queries,
            max_workers=args.workers,
            questions_file=args.questions_file,
        )
        all_test_results.append(test_result)
        print_metrics_report(test_result)

        # Small delay between tests
        if num_queries != query_counts[-1]:
            print("\nWaiting 5 seconds before next test...")
            time.sleep(5)

    # Analysis
    identify_bottlenecks(all_test_results)
    provide_optimization_recommendations(all_test_results)

    # Save results
    save_results(all_test_results, args.output)

    print(f"\n{'='*60}")
    print("LOAD TEST COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
