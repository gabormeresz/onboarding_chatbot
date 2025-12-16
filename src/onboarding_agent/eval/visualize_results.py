#!/usr/bin/env python3
"""
Generate visualization and detailed report from evaluation results.

Usage:
    python visualize_results.py [eval_results.json]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_results(filepath: str) -> Dict:
    """Load evaluation results from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def print_detailed_report(data: Dict):
    """Print a detailed textual report of evaluation results."""
    summary = data["summary"]
    results = data["detailed_results"]

    print("\n" + "=" * 80)
    print("DETAILED EVALUATION REPORT")
    print("=" * 80)

    # Summary section
    print(f"\n📊 OVERALL RESULTS")
    print(f"   Total Tests: {summary['total_tests']}")
    print(
        f"   Passed: {summary['passed_tests']} ({summary['overall_accuracy']*100:.1f}%)"
    )
    print(f"   Failed: {summary['failed_tests']}")

    # Routing breakdown
    print(f"\n🎯 ROUTING METRICS")
    print(f"   Overall Accuracy:      {summary['overall_accuracy']*100:>6.1f}%")
    print(f"   F1 Score:              {summary.get('f1_score', 0)*100:>6.1f}%")

    # Category breakdown with N/A handling
    resp_gen_str = (
        f"{summary['response_generation_accuracy']*100:>6.1f}%"
        if summary["response_generation_accuracy"] is not None
        else "N/A (no test cases)"
    )
    esc_det_str = (
        f"{summary['escalation_detection_accuracy']*100:>6.1f}%"
        if summary["escalation_detection_accuracy"] is not None
        else "N/A (no test cases)"
    )
    print(f"   Response Gen Cases:    {resp_gen_str}")
    print(f"   Escalation Detection:  {esc_det_str}")

    # Performance
    print(f"\n⚡ PERFORMANCE")
    print(f"   Average Latency: {summary['avg_latency']:.3f}s")
    print(f"   Min Latency:     {summary['min_latency']:.3f}s")
    print(f"   Max Latency:     {summary['max_latency']:.3f}s")

    # Quality metrics if available
    if summary.get("avg_relevance", 0) > 0:
        print(f"\n✨ QUALITY METRICS (LLM-Judged)")
        print(f"   Answer Relevance:      {summary['avg_relevance']*100:>6.1f}%")
        print(f"   Answer Completeness:   {summary['avg_completeness']*100:>6.1f}%")

    # Failed tests details
    failed_results = [
        r for r in results if not (r["route_correct"] and r["escalation_correct"])
    ]
    if failed_results:
        print(f"\n❌ FAILED TESTS ({len(failed_results)})")
        print("-" * 80)
        for result in failed_results:
            print(f"\n   Test #{result['question_id']}")
            print(f"   Q: {result['question']}")
            print(
                f"   Expected: route={result['expected_route']}, escalate={result['expected_escalation']}"
            )
            print(
                f"   Got:      route={result['actual_route']}, escalate={result['actual_escalation']}"
            )
            print(
                f"   Issues:   {'Route ❌' if not result['route_correct'] else 'Route ✓'} | "
                f"{'Escalation ❌' if not result['escalation_correct'] else 'Escalation ✓'}"
            )
            if result.get("error"):
                print(f"   Error: {result['error']}")

    # Passed tests by category
    response_gen_results = [
        r for r in results if r["expected_route"] == "response_generation"
    ]
    escalation_results = [r for r in results if r["expected_route"] == "escalation"]

    passed_response_gen = [
        r
        for r in response_gen_results
        if r["route_correct"] and r["escalation_correct"]
    ]
    passed_escalations = [
        r for r in escalation_results if r["route_correct"] and r["escalation_correct"]
    ]

    print(f"\n✅ PASSED TESTS BY CATEGORY")
    resp_gen_pct = (
        f"{len(passed_response_gen)/len(response_gen_results)*100:.1f}%"
        if response_gen_results
        else "N/A"
    )
    esc_det_pct = (
        f"{len(passed_escalations)/len(escalation_results)*100:.1f}%"
        if escalation_results
        else "N/A"
    )
    print(
        f"   Response Generation: {len(passed_response_gen)}/{len(response_gen_results)} ({resp_gen_pct})"
    )
    print(
        f"   Escalation Detection: {len(passed_escalations)}/{len(escalation_results)} ({esc_det_pct})"
    )

    # Latency distribution
    print(f"\n⏱️  LATENCY DISTRIBUTION")
    latencies = [r["latency_seconds"] for r in results]
    latencies.sort()

    # Calculate percentiles
    def percentile(data, p):
        k = (len(data) - 1) * p
        f = int(k)
        c = k - f
        if f + 1 < len(data):
            return data[f] + (data[f + 1] - data[f]) * c
        return data[f]

    print(f"   P50 (median): {percentile(latencies, 0.50):.3f}s")
    print(f"   P90:          {percentile(latencies, 0.90):.3f}s")
    print(f"   P95:          {percentile(latencies, 0.95):.3f}s")
    print(f"   P99:          {percentile(latencies, 0.99):.3f}s")

    # Slowest queries
    sorted_by_latency = sorted(
        results, key=lambda x: x["latency_seconds"], reverse=True
    )
    print(f"\n🐌 SLOWEST QUERIES (Top 3)")
    for i, result in enumerate(sorted_by_latency[:3], 1):
        print(
            f"   {i}. {result['latency_seconds']:.3f}s - Test #{result['question_id']}"
        )
        print(f"      {result['question'][:70]}...")

    # Test coverage summary
    print(f"\n📋 TEST COVERAGE")
    print(f"   Standard Questions:     {len(response_gen_results)} tests")
    print(f"   Critical Escalations:   {len(escalation_results)} tests")
    print(f"   Total Cases:       {summary['total_tests']} tests")

    print("\n" + "=" * 80 + "\n")


def generate_ascii_chart(data: List[tuple], title: str, width: int = 50):
    """Generate simple ASCII bar chart."""
    print(f"\n{title}")
    print("-" * (width + 20))

    # Filter out None values
    valid_data = [(label, value) for label, value in data if value is not None]

    if not valid_data:
        print("  No data available")
        print()
        return

    max_value = max(v for _, v in valid_data)

    for label, value in data:
        if value is None:
            print(f"{label:25} N/A (no test cases)")
        else:
            bar_length = int((value / max_value) * width) if max_value > 0 else 0
            bar = "█" * bar_length
            percentage = value * 100 if value <= 1 else value
            print(f"{label:25} {bar} {percentage:5.1f}%")

    print()


def main():
    if len(sys.argv) < 2:
        results_file = "eval_results.json"
    else:
        results_file = sys.argv[1]

    if not Path(results_file).exists():
        print(f"ERROR: Results file '{results_file}' not found.")
        print(f"Usage: python visualize_results.py [results_file.json]")
        sys.exit(1)

    print(f"Loading results from: {results_file}")
    data = load_results(results_file)

    # Print detailed report
    print_detailed_report(data)

    # Generate ASCII charts
    summary = data["summary"]

    generate_ascii_chart(
        [
            ("Overall Accuracy", summary["overall_accuracy"]),
            ("F1 Score", summary.get("f1_score", 0)),
        ],
        "📊 ACCURACY METRICS",
    )

    generate_ascii_chart(
        [
            ("Response Gen Cases", summary["response_generation_accuracy"]),
            ("Escalation Detection", summary["escalation_detection_accuracy"]),
        ],
        "📂 CATEGORY BREAKDOWN",
    )

    print("=" * 80)
    print("Report generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
