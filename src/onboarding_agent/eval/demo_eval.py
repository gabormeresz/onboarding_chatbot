#!/usr/bin/env python3
"""
Quick demo/test of the evaluation framework.
Runs on a subset of questions for demonstration.
"""

from onboarding_agent.eval.evaluate_graph import GraphEvaluator, EvaluationSummary


def main():
    print("=" * 70)
    print("EVALUATION FRAMEWORK DEMO")
    print("=" * 70)
    print("\nThis demo runs a subset of questions to verify the framework.")
    print("For full evaluation, use: python run_eval.py\n")

    # Initialize evaluator without LLM judges for speed
    evaluator = GraphEvaluator(use_llm_judges=False)

    # Create a small test set
    demo_cases = [
        {
            "id": 1,
            "question": "How many home office days per week am I currently allowed to take?",
            "expected": {"route": "response_generation", "escalation": False},
        },
        {
            "id": 15,
            "question": "I received an email asking for my password and VPN details. What should I do immediately?",
            "expected": {"route": "escalation", "escalation": True},
        },
    ]

    print("Running 2 demo test cases...\n")

    # Create summary object
    summary = EvaluationSummary()
    summary.total_tests = len(demo_cases)

    for test_case in demo_cases:
        print(f"Testing: {test_case['question'][:60]}...")
        result = evaluator.run_single_test(test_case)
        summary.results.append(result)

        status = "✓ PASS" if result.overall_correct() else "✗ FAIL"
        print(f"  {status} | Latency: {result.latency_seconds:.2f}s")
        print(
            f"  Route correct: {result.route_correct} | Escalation correct: {result.escalation_correct}"
        )
        print(f"  Answer: {result.answer[:100]}...")
        print()

    # Calculate metrics
    summary.passed_tests = sum(1 for r in summary.results if r.overall_correct())
    summary.failed_tests = summary.total_tests - summary.passed_tests

    summary.overall_accuracy = (
        summary.passed_tests / summary.total_tests if summary.total_tests > 0 else 0
    )

    # Calculate F1 score
    true_positives = sum(
        1 for r in summary.results if r.expected_escalation and r.actual_escalation
    )
    false_positives = sum(
        1 for r in summary.results if not r.expected_escalation and r.actual_escalation
    )
    false_negatives = sum(
        1 for r in summary.results if r.expected_escalation and not r.actual_escalation
    )

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0
    )
    summary.f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    # Category breakdown
    response_gen_cases = [
        r for r in summary.results if r.expected_route == "response_generation"
    ]
    escalation_cases = [r for r in summary.results if r.expected_route == "escalation"]

    if response_gen_cases:
        summary.response_generation_accuracy = sum(
            1 for r in response_gen_cases if r.overall_correct()
        ) / len(response_gen_cases)
    else:
        summary.response_generation_accuracy = None

    if escalation_cases:
        summary.escalation_detection_accuracy = sum(
            1 for r in escalation_cases if r.overall_correct()
        ) / len(escalation_cases)
    else:
        summary.escalation_detection_accuracy = None

    # Performance metrics
    latencies = [r.latency_seconds for r in summary.results]
    if latencies:
        summary.avg_latency = sum(latencies) / len(latencies)
        summary.min_latency = min(latencies)
        summary.max_latency = max(latencies)

    # Print summary
    print("=" * 70)
    print("DEMO RESULTS")
    print("=" * 70)
    print(f"\nTotal Tests: {summary.total_tests}")
    print(f"Passed: {summary.passed_tests} ({summary.overall_accuracy*100:.1f}%)")
    print(f"Failed: {summary.failed_tests}")

    print(f"\n--- Routing Metrics ---")
    print(f"Overall Accuracy: {summary.overall_accuracy*100:.1f}%")
    print(f"F1 Score: {summary.f1_score*100:.1f}%")

    # Category breakdown with N/A handling
    resp_gen_str = (
        f"{summary.response_generation_accuracy*100:.1f}%"
        if summary.response_generation_accuracy is not None
        else "N/A (no test cases)"
    )
    esc_det_str = (
        f"{summary.escalation_detection_accuracy*100:.1f}%"
        if summary.escalation_detection_accuracy is not None
        else "N/A (no test cases)"
    )
    print(f"Response Generation Cases: {resp_gen_str}")
    print(f"Escalation Detection Cases: {esc_det_str}")

    print(f"\n--- Performance Metrics ---")
    print(f"Average Latency: {summary.avg_latency:.3f}s")
    print(f"Min Latency: {summary.min_latency:.3f}s")
    print(f"Max Latency: {summary.max_latency:.3f}s")

    print("\n" + "=" * 70)
    print("\nFor complete evaluation with all 18 test cases:")
    print("  PYTHONPATH=src python src/onboarding_agent/eval/run_eval.py")
    print()


if __name__ == "__main__":
    main()
