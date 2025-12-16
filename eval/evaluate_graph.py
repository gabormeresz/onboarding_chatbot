"""
Evaluation framework for the onboarding agent LangGraph.

This module provides comprehensive evaluation metrics for assessing:
- Routing accuracy (correct intent classification and path selection)
- Answer quality (relevance, completeness, correctness)
- Escalation correctness (proper identification of critical issues)
- System performance (latency, retrieval quality)

Designed for technical assessment demonstration.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict

from onboarding_agent.agent.graph import build_graph
from onboarding_agent.agent.state import build_initial_state, AgentState
from onboarding_agent.models.chat import get_chat_model


@dataclass
class EvaluationResult:
    """Container for individual test case evaluation results."""

    question_id: int
    question: str
    expected_route: str
    expected_escalation: bool

    # Actual results
    actual_route: str
    actual_escalation: bool
    answer: str

    # Metrics
    route_correct: bool
    escalation_correct: bool
    latency_seconds: float

    # Optional quality scores
    answer_relevance_score: float = 0.0
    answer_completeness_score: float = 0.0

    # Additional context
    intent_classified: str = ""
    retrieved_docs_count: int = 0
    ticket_created: bool = False
    error: str = ""

    def overall_correct(self) -> bool:
        """Check if routing and escalation are both correct."""
        return self.route_correct and self.escalation_correct

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class EvaluationSummary:
    """Aggregated metrics across all test cases."""

    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0

    # Routing metrics
    overall_accuracy: float = 0.0
    f1_score: float = 0.0  # F1 score for imbalanced datasets

    # Performance metrics
    avg_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0

    # Quality metrics
    avg_relevance: float = 0.0
    avg_completeness: float = 0.0

    # Category breakdown (None if category not in test set)
    response_generation_accuracy: Optional[float] = None
    escalation_detection_accuracy: Optional[float] = None

    results: List[EvaluationResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding full results list."""
        data = asdict(self)
        # Remove detailed results from summary dict
        data.pop("results", None)
        return data


class GraphEvaluator:
    """Evaluator for the onboarding agent LangGraph."""

    def __init__(self, use_llm_judges: bool = False):
        """
        Initialize the evaluator.

        Args:
            use_llm_judges: If True, use LLM-as-judge for answer quality evaluation.
                          This is slower but provides quality scores.
        """
        self.graph = build_graph()
        self.use_llm_judges = use_llm_judges
        if use_llm_judges:
            self.judge_llm = get_chat_model()

    def load_test_questions(self, jsonl_path: str) -> List[Dict[str, Any]]:
        """Load test questions from JSONL file."""
        questions = []
        with open(jsonl_path, "r") as f:
            for line in f:
                if line.strip():
                    questions.append(json.loads(line))
        return questions

    def run_single_test(self, test_case: Dict[str, Any]) -> EvaluationResult:
        """
        Run a single test case through the graph.

        Args:
            test_case: Dictionary with 'id', 'question', and 'expected' fields

        Returns:
            EvaluationResult with all metrics populated
        """
        question_id = test_case["id"]
        question = test_case["question"]
        expected = test_case["expected"]
        expected_route = expected["route"]
        expected_escalation = expected["escalation"]

        # Initialize result
        result = EvaluationResult(
            question_id=question_id,
            question=question,
            expected_route=expected_route,
            expected_escalation=expected_escalation,
            actual_route="unknown",
            actual_escalation=False,
            answer="",
            route_correct=False,
            escalation_correct=False,
            latency_seconds=0.0,
        )

        try:
            # Run the graph and measure latency
            start_time = time.time()
            initial_state = build_initial_state(user_query=question)
            final_state = self.graph.invoke(initial_state)
            end_time = time.time()

            result.latency_seconds = end_time - start_time

            # Extract actual results from state
            result.actual_route = final_state.get("route_decision", "unknown")
            result.actual_escalation = final_state.get("needs_escalation", False)
            result.answer = final_state.get("answer", "")
            result.intent_classified = final_state.get("intent", "")
            result.retrieved_docs_count = len(final_state.get("retrieved_docs", []))
            result.ticket_created = final_state.get("ticket_info") is not None

            # Evaluate correctness
            result.route_correct = self._check_route_correctness(
                expected_route, result.actual_route, result.actual_escalation
            )
            result.escalation_correct = result.actual_escalation == expected_escalation

            # Optional: LLM-as-judge for answer quality
            if self.use_llm_judges and result.answer:
                result.answer_relevance_score = self._judge_answer_relevance(
                    question, result.answer
                )
                result.answer_completeness_score = self._judge_answer_completeness(
                    question, result.answer
                )

        except Exception as e:
            result.error = str(e)
            print(f"Error in test {question_id}: {e}")

        return result

    def _check_route_correctness(
        self, expected_route: str, actual_route: str, actual_escalation: bool
    ) -> bool:
        """
        Check if routing decision is correct.

        Maps expected behavior to actual route_decision values.
        Expected 'response_generation' should not escalate.
        Expected 'escalation' should escalate.
        """
        if expected_route == "escalation":
            return actual_escalation
        elif expected_route == "response_generation":
            # Should NOT escalate, and should use response generation path
            return not actual_escalation
        else:
            # Unknown expected route
            return actual_route == expected_route

    def _judge_answer_relevance(self, question: str, answer: str) -> float:
        """
        Use LLM to judge answer relevance to question.
        Returns score between 0.0 and 1.0.
        """
        prompt = f"""Rate how relevant this answer is to the question on a scale of 0-10.

Question: {question}

Answer: {answer}

Provide only a number between 0 and 10, where:
- 0 = completely irrelevant or no answer
- 5 = partially relevant
- 10 = highly relevant and directly addresses the question

Score:"""

        try:
            response = self.judge_llm.invoke(prompt)
            content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )
            score_text = content.strip()
            score = float(score_text.split()[0])  # Extract first number
            return min(max(score / 10.0, 0.0), 1.0)  # Normalize to 0-1
        except Exception as e:
            print(f"Error judging relevance: {e}")
            return 0.0

    def _judge_answer_completeness(self, question: str, answer: str) -> float:
        """
        Use LLM to judge answer completeness.
        Returns score between 0.0 and 1.0.
        """
        prompt = f"""Rate how complete this answer is on a scale of 0-10.

Question: {question}

Answer: {answer}

Provide only a number between 0 and 10, where:
- 0 = no useful information
- 5 = partially complete
- 10 = comprehensive and complete

Score:"""

        try:
            response = self.judge_llm.invoke(prompt)
            content = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )
            score_text = content.strip()
            score = float(score_text.split()[0])
            return min(max(score / 10.0, 0.0), 1.0)
        except Exception as e:
            print(f"Error judging completeness: {e}")
            return 0.0

    def run_evaluation(self, jsonl_path: str) -> EvaluationSummary:
        """
        Run full evaluation on all test cases.

        Args:
            jsonl_path: Path to JSONL file with test questions

        Returns:
            EvaluationSummary with aggregated metrics
        """
        print(f"Loading test cases from {jsonl_path}...")
        test_cases = self.load_test_questions(jsonl_path)
        print(f"Running evaluation on {len(test_cases)} test cases...\n")

        summary = EvaluationSummary()
        summary.total_tests = len(test_cases)

        # Run all test cases
        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] Testing: {test_case['question'][:60]}...")
            result = self.run_single_test(test_case)
            summary.results.append(result)

            if result.error:
                summary.errors.append(f"Test {result.question_id}: {result.error}")

            # Print result
            status = "✓ PASS" if result.overall_correct() else "✗ FAIL"
            print(
                f"  {status} | Route: {result.route_correct} | Escalation: {result.escalation_correct} | {result.latency_seconds:.2f}s"
            )
            if not result.overall_correct():
                print(
                    f"    Expected: route={result.expected_route}, escalate={result.expected_escalation}"
                )
                print(
                    f"    Got: route={result.actual_route}, escalate={result.actual_escalation}"
                )
            print()

        # Calculate aggregate metrics
        summary.passed_tests = sum(1 for r in summary.results if r.overall_correct())
        summary.failed_tests = summary.total_tests - summary.passed_tests

        # Overall accuracy
        summary.overall_accuracy = (
            summary.passed_tests / summary.total_tests if summary.total_tests > 0 else 0
        )

        # Calculate F1 score for imbalanced datasets
        # F1 = 2 * (precision * recall) / (precision + recall)
        # For binary classification: escalation vs non-escalation
        true_positives = sum(
            1 for r in summary.results if r.expected_escalation and r.actual_escalation
        )
        false_positives = sum(
            1
            for r in summary.results
            if not r.expected_escalation and r.actual_escalation
        )
        false_negatives = sum(
            1
            for r in summary.results
            if r.expected_escalation and not r.actual_escalation
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

        # Category breakdown (set to None if category has no test cases)
        response_gen_cases = [
            r for r in summary.results if r.expected_route == "response_generation"
        ]
        escalation_cases = [
            r for r in summary.results if r.expected_route == "escalation"
        ]

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

        # Quality metrics (if LLM judges used)
        if self.use_llm_judges:
            relevance_scores = [
                r.answer_relevance_score
                for r in summary.results
                if r.answer_relevance_score > 0
            ]
            completeness_scores = [
                r.answer_completeness_score
                for r in summary.results
                if r.answer_completeness_score > 0
            ]

            if relevance_scores:
                summary.avg_relevance = sum(relevance_scores) / len(relevance_scores)
            if completeness_scores:
                summary.avg_completeness = sum(completeness_scores) / len(
                    completeness_scores
                )

        return summary

    def print_summary(self, summary: EvaluationSummary):
        """Print evaluation summary in a formatted way."""
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
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

        if self.use_llm_judges:
            print(f"\n--- Quality Metrics (LLM-Judged) ---")
            print(f"Average Relevance: {summary.avg_relevance*100:.1f}%")
            print(f"Average Completeness: {summary.avg_completeness*100:.1f}%")

        if summary.errors:
            print(f"\n--- Errors ({len(summary.errors)}) ---")
            for error in summary.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(summary.errors) > 5:
                print(f"  ... and {len(summary.errors) - 5} more")

        print("\n" + "=" * 70)

    def save_results(self, summary: EvaluationSummary, output_path: str):
        """Save detailed results to JSON file."""
        output_data = {
            "summary": summary.to_dict(),
            "detailed_results": [r.to_dict() for r in summary.results],
            "errors": summary.errors,
        }

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\nDetailed results saved to: {output_path}")
