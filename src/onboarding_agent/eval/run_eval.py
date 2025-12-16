#!/usr/bin/env python3
"""
Main script to run the evaluation framework for the onboarding agent.

Usage:
    python run_eval.py [--use-llm-judges] [--output results.json]

Options:
    --use-llm-judges    Enable LLM-as-judge for answer quality evaluation (slower)
    --output FILE       Save detailed results to JSON file (default: src/onboarding_agent/eval/results/eval_results.json)
"""

import argparse
import sys
from pathlib import Path

from onboarding_agent.eval.evaluate_graph import GraphEvaluator


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluation on the onboarding agent LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic evaluation (routing and escalation accuracy only)
  python run_eval.py
  
  # With LLM-as-judge for answer quality (slower but more comprehensive)
  python run_eval.py --use-llm-judges
  
  # Save results to custom file
  python run_eval.py --output my_results.json
        """,
    )

    parser.add_argument(
        "--use-llm-judges",
        action="store_true",
        help="Use LLM-as-judge for answer quality evaluation (slower)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="src/onboarding_agent/eval/results/eval_results.json",
        help="Output file for detailed results (default: src/onboarding_agent/eval/results/eval_results.json)",
    )

    parser.add_argument(
        "--questions",
        type=str,
        default=None,
        help="Path to questions JSONL file (default: auto-detect)",
    )

    args = parser.parse_args()

    # Find questions file
    if args.questions:
        questions_path = args.questions
    else:
        # Auto-detect based on common locations
        candidates = [
            "src/onboarding_agent/eval/questions.jsonl",
            "questions.jsonl",
            "../eval/questions.jsonl",
        ]
        questions_path = None
        for candidate in candidates:
            if Path(candidate).exists():
                questions_path = candidate
                break

        if not questions_path:
            print("ERROR: Could not find questions.jsonl file.")
            print("Please specify the path using --questions option.")
            sys.exit(1)

    print("=" * 70)
    print("ONBOARDING AGENT EVALUATION")
    print("=" * 70)
    print(f"\nQuestions file: {questions_path}")
    print(f"LLM judges: {'Enabled' if args.use_llm_judges else 'Disabled'}")
    print(f"Output file: {args.output}")
    print()

    # Initialize evaluator
    evaluator = GraphEvaluator(use_llm_judges=args.use_llm_judges)

    # Run evaluation
    try:
        summary = evaluator.run_evaluation(questions_path)

        # Print summary
        evaluator.print_summary(summary)

        # Save results
        evaluator.save_results(summary, args.output)

        # Exit with appropriate code
        if summary.failed_tests > 0:
            print(f"\n⚠ Evaluation completed with {summary.failed_tests} failures")
            sys.exit(1)
        else:
            print("\n✓ All tests passed!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERROR: Evaluation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
