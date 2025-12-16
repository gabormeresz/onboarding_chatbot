#!/usr/bin/env python3
"""
Generate visualization and detailed report from load test results.

Usage:
    python visualize_load_results.py [load_test_results.json]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_results(filepath: str) -> List[Dict]:
    """Load load test results from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def generate_ascii_chart(
    data: List[tuple], title: str, width: int = 50, unit: str = ""
):
    """Generate simple ASCII bar chart."""
    print(f"\n{title}")
    print("-" * (width + 30))

    if not data:
        print("  No data available")
        print()
        return

    max_value = max(v for _, v in data)

    for label, value in data:
        bar_length = int((value / max_value) * width) if max_value > 0 else 0
        bar = "█" * bar_length
        print(f"{label:20} {bar} {value:8.2f}{unit}")

    print()


def generate_latency_chart(latencies: List[tuple], title: str, width: int = 50):
    """Generate ASCII chart for latency metrics."""
    print(f"\n{title}")
    print("-" * (width + 30))

    if not latencies:
        print("  No data available")
        print()
        return

    max_value = max(v for _, v in latencies)

    for label, value in latencies:
        bar_length = int((value / max_value) * width) if max_value > 0 else 0
        bar = "█" * bar_length
        print(f"{label:20} {bar} {value:8.3f}s")

    print()


def print_detailed_report(all_results: List[Dict]):
    """Print a detailed textual report of load test results."""

    print("\n" + "=" * 80)
    print("DETAILED LOAD TEST REPORT")
    print("=" * 80)

    # Overall Summary
    print(f"\n📊 TEST SUMMARY")
    print(f"   Total Test Runs: {len(all_results)}")
    print(
        f"   Query Counts Tested: {', '.join(str(r['num_queries']) for r in all_results)}"
    )

    total_queries = sum(r["num_queries"] for r in all_results)
    total_successful = sum(r["metrics"]["successful_queries"] for r in all_results)
    total_failed = sum(r["metrics"]["failed_queries"] for r in all_results)
    overall_success_rate = (
        (total_successful / total_queries * 100) if total_queries > 0 else 0
    )

    print(f"   Total Queries Executed: {total_queries}")
    print(f"   Successful: {total_successful} ({overall_success_rate:.1f}%)")
    print(f"   Failed: {total_failed}")

    # Performance Trends
    print(f"\n⚡ PERFORMANCE TRENDS")
    print("-" * 80)
    print(
        f"{'Queries':<12} {'Workers':<10} {'Mean Lat':<12} {'P95 Lat':<12} {'Throughput':<15} {'Success %':<12}"
    )
    print("-" * 80)

    for result in all_results:
        metrics = result["metrics"]
        print(
            f"{result['num_queries']:<12} "
            f"{result['max_workers']:<10} "
            f"{metrics['latency']['mean']:<12.3f} "
            f"{metrics['latency']['p95']:<12.3f} "
            f"{metrics['throughput']['queries_per_second']:<15.2f} "
            f"{metrics['success_rate']:<12.1f}"
        )

    # Latency Analysis for largest test
    largest_test = max(all_results, key=lambda x: x["num_queries"])
    metrics = largest_test["metrics"]

    print(
        f"\n⏱️  DETAILED LATENCY METRICS (from {largest_test['num_queries']} query test)"
    )
    latency = metrics["latency"]
    print(f"   Min:      {latency['min']:>8.3f}s")
    print(f"   Max:      {latency['max']:>8.3f}s")
    print(f"   Mean:     {latency['mean']:>8.3f}s")
    print(f"   Median:   {latency['median']:>8.3f}s")
    print(f"   P50:      {latency['p50']:>8.3f}s")
    print(f"   P95:      {latency['p95']:>8.3f}s")
    print(f"   P99:      {latency['p99']:>8.3f}s")
    print(f"   StdDev:   {latency['stdev']:>8.3f}s")

    # Route Distribution
    print(f"\n🎯 ROUTE DISTRIBUTION (from {largest_test['num_queries']} query test)")
    route_dist = metrics.get("route_distribution", {})
    total_success = metrics["successful_queries"]

    if route_dist:
        print("-" * 80)
        for route, count in sorted(
            route_dist.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / total_success * 100) if total_success > 0 else 0
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_length
            print(f"   {route:20} {bar} {count:4} ({percentage:5.1f}%)")
    else:
        print("   No route distribution data available")

    # Bottleneck Analysis
    print(f"\n🔍 BOTTLENECK ANALYSIS")
    print("-" * 80)

    if len(all_results) >= 2:
        first_result = all_results[0]
        last_result = all_results[-1]

        first_mean = first_result["metrics"]["latency"]["mean"]
        last_mean = last_result["metrics"]["latency"]["mean"]
        growth_factor = last_mean / first_mean if first_mean > 0 else 0

        print(f"   Latency Growth:")
        print(f"      {first_result['num_queries']} queries: {first_mean:.3f}s mean")
        print(f"      {last_result['num_queries']} queries: {last_mean:.3f}s mean")
        print(f"      Growth Factor: {growth_factor:.2f}x")

        if growth_factor > 1.5:
            print(f"      ⚠️  HIGH GROWTH - System doesn't scale linearly")
            print(f"      → Primary Bottleneck: Sequential LLM processing")
        elif growth_factor > 1.2:
            print(f"      ⚠️  MODERATE GROWTH - Some scaling limitations")
        else:
            print(f"      ✓  GOOD SCALING - System handles load well")

        # Throughput analysis
        max_throughput = max(
            r["metrics"]["throughput"]["queries_per_second"] for r in all_results
        )
        print(f"\n   Maximum Throughput: {max_throughput:.2f} queries/sec")

        if max_throughput < 1.0:
            print(f"      ⚠️  VERY LOW - Severe sequential bottleneck")
        elif max_throughput < 2.0:
            print(f"      ⚠️  LOW - Limited by model inference")
        elif max_throughput < 5.0:
            print(f"      →  MODERATE - Acceptable for prototype")
        else:
            print(f"      ✓  GOOD - Efficient processing")

    # Performance Degradation
    if len(all_results) >= 2:
        print(f"\n   Performance Degradation:")
        baseline_throughput = all_results[0]["metrics"]["throughput"][
            "queries_per_second"
        ]

        for result in all_results[1:]:
            current_throughput = result["metrics"]["throughput"]["queries_per_second"]
            degradation = (
                ((baseline_throughput - current_throughput) / baseline_throughput * 100)
                if baseline_throughput > 0
                else 0
            )

            if degradation > 20:
                status = "⚠️"
            elif degradation > 10:
                status = "→"
            else:
                status = "✓"

            print(
                f"      {status} At {result['num_queries']} queries: {degradation:+.1f}% from baseline"
            )

    # Failure Analysis
    print(f"\n❌ FAILURE ANALYSIS")

    any_failures = any(r["metrics"]["failed_queries"] > 0 for r in all_results)

    if any_failures:
        print("-" * 80)
        for result in all_results:
            if result["metrics"]["failed_queries"] > 0:
                print(f"\n   Test with {result['num_queries']} queries:")
                print(f"      Failed: {result['metrics']['failed_queries']}")
                print(f"      Success Rate: {result['metrics']['success_rate']:.1f}%")

                # Show sample failures if available
                if result.get("sample_failures"):
                    print(f"      Sample Failures:")
                    for failure in result["sample_failures"][:3]:
                        print(
                            f"         - Query #{failure['query_id']}: {failure['error'][:60]}..."
                        )
    else:
        print("   ✓ No failures detected across all tests")

    print("\n" + "=" * 80 + "\n")


def print_optimization_recommendations(all_results: List[Dict]):
    """Print optimization recommendations based on test results."""

    print("\n" + "=" * 80)
    print("🚀 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    largest_test = max(all_results, key=lambda x: x["num_queries"])
    metrics = largest_test["metrics"]

    recommendations = []

    # 1. Model optimization
    mean_latency = metrics["latency"]["mean"]
    if mean_latency > 5.0:
        priority = "🔴 CRITICAL"
        impact = "60-80%"
    elif mean_latency > 3.0:
        priority = "🟡 HIGH"
        impact = "40-60%"
    else:
        priority = "🟢 MEDIUM"
        impact = "20-40%"

    recommendations.append(
        {
            "priority": priority,
            "title": "Model Optimization",
            "issue": f"Mean latency: {mean_latency:.2f}s per query",
            "recommendation": "Switch to faster model (qwen2.5:3b or llama3.2:3b)",
            "expected_impact": f"{impact} latency reduction",
            "steps": [
                "Update models/config.py to use smaller model",
                "Benchmark accuracy vs speed tradeoff",
                "Consider streaming responses for better UX",
            ],
        }
    )

    # 2. Caching
    route_dist = metrics.get("route_distribution", {})
    rag_percentage = (
        (route_dist.get("needs_rag", 0) / metrics["successful_queries"] * 100)
        if metrics["successful_queries"] > 0
        else 0
    )

    if rag_percentage > 50:
        priority = "🟡 HIGH"
    elif rag_percentage > 30:
        priority = "🟢 MEDIUM"
    else:
        priority = "⚪ LOW"

    if rag_percentage > 20:
        recommendations.append(
            {
                "priority": priority,
                "title": "Response Caching",
                "issue": f"{rag_percentage:.1f}% of queries use expensive RAG",
                "recommendation": "Implement semantic caching for RAG responses",
                "expected_impact": "30-50% faster for similar queries",
                "steps": [
                    "Use LangChain SemanticCache with ChromaDB",
                    "Cache responses based on query embedding similarity",
                    "Set appropriate TTL (1-4 hours)",
                    "Monitor cache hit rate",
                ],
            }
        )

    # 3. Parallel processing
    throughput = metrics["throughput"]["queries_per_second"]
    if throughput < 2.0:
        priority = "🟡 HIGH"
        impact = "2-3x"
    elif throughput < 5.0:
        priority = "🟢 MEDIUM"
        impact = "1.5-2x"
    else:
        priority = "⚪ LOW"
        impact = "1.2-1.5x"

    recommendations.append(
        {
            "priority": priority,
            "title": "Async/Parallel Processing",
            "issue": f"Low throughput: {throughput:.2f} queries/sec",
            "recommendation": "Enable async processing with multiple Ollama instances",
            "expected_impact": f"{impact} throughput increase",
            "steps": [
                "Set OLLAMA_NUM_PARALLEL=4 in environment",
                "Convert graph.invoke() to graph.ainvoke()",
                "Use asyncio.gather() for concurrent requests",
                "Consider load balancing across multiple Ollama servers",
            ],
        }
    )

    # 4. RAG optimization
    recommendations.append(
        {
            "priority": "⚪ LOW",
            "title": "RAG Performance Tuning",
            "issue": "Vector search and retrieval can be optimized",
            "recommendation": "Optimize ChromaDB configuration and retrieval",
            "expected_impact": "10-20% faster RAG queries",
            "steps": [
                "Use HNSW index for faster similarity search",
                "Reduce k (retrieved docs) from 4 to 3",
                "Add metadata pre-filtering",
                "Consider using faster embedding model",
            ],
        }
    )

    # Print recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']}] {rec['title']}")
        print(f"   Issue: {rec['issue']}")
        print(f"   💡 Recommendation: {rec['recommendation']}")
        print(f"   📈 Expected Impact: {rec['expected_impact']}")
        print(f"   Implementation Steps:")
        for step in rec["steps"]:
            print(f"      • {step}")

    print("\n" + "=" * 80 + "\n")


def main():
    if len(sys.argv) < 2:
        results_file = "loadtest/results/load_test_results.json"
    else:
        results_file = sys.argv[1]

    if not Path(results_file).exists():
        print(f"ERROR: Results file '{results_file}' not found.")
        print(f"Usage: python visualize_load_results.py [results_file.json]")
        sys.exit(1)

    print(f"Loading results from: {results_file}")
    all_results = load_results(results_file)

    # Print detailed report
    print_detailed_report(all_results)

    # Generate ASCII charts
    if all_results:
        largest_test = max(all_results, key=lambda x: x["num_queries"])
        latency = largest_test["metrics"]["latency"]

        # Latency distribution chart
        generate_latency_chart(
            [
                ("Min", latency["min"]),
                ("P50 (Median)", latency["p50"]),
                ("Mean", latency["mean"]),
                ("P95", latency["p95"]),
                ("P99", latency["p99"]),
                ("Max", latency["max"]),
            ],
            f"⏱️  LATENCY DISTRIBUTION ({largest_test['num_queries']} queries)",
        )

        # Throughput comparison
        generate_ascii_chart(
            [
                (
                    f"{r['num_queries']} queries",
                    r["metrics"]["throughput"]["queries_per_second"],
                )
                for r in all_results
            ],
            "📊 THROUGHPUT COMPARISON",
            unit=" q/s",
        )

        # Mean latency comparison
        generate_latency_chart(
            [
                (f"{r['num_queries']} queries", r["metrics"]["latency"]["mean"])
                for r in all_results
            ],
            "📈 MEAN LATENCY TREND",
        )

    # Print optimization recommendations
    print_optimization_recommendations(all_results)

    print("=" * 80)
    print("✅ Load test report generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
