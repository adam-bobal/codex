"""
Batch and Comparative Prompt Evaluation
For A/B testing prompts or iterating on versions.
"""

from prompt_evaluator import PromptEvaluator, EvaluationResult
from typing import Optional
import json


class PromptComparator:
    """Compare multiple prompts or track iterations."""
    
    def __init__(self):
        self.evaluator = PromptEvaluator()
        self.history: list[tuple[str, EvaluationResult]] = []
    
    def compare(self, prompts: list[str], labels: Optional[list[str]] = None) -> dict:
        """
        Compare multiple prompts side by side.
        
        Args:
            prompts: List of prompt strings
            labels: Optional names for each prompt (e.g., ["v1", "v2"])
        
        Returns:
            Comparison report with winner and breakdown
        """
        if labels is None:
            labels = [f"Prompt {i+1}" for i in range(len(prompts))]
        
        results = []
        for prompt, label in zip(prompts, labels):
            result = self.evaluator.evaluate(prompt)
            results.append({
                "label": label,
                "score": result.overall_score,
                "clarity": result.clarity_score,
                "specificity": result.specificity_score,
                "structure": result.structure_score,
                "completeness": result.completeness_score,
                "type": result.prompt_type,
                "tokens": result.token_estimate,
                "weaknesses": result.weaknesses,
                "suggestions": result.suggestions
            })
            self.history.append((label, result))
        
        # Determine winner
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        winner = sorted_results[0]
        
        return {
            "winner": winner["label"],
            "winner_score": winner["score"],
            "margin": round(winner["score"] - sorted_results[1]["score"], 1) if len(sorted_results) > 1 else 0,
            "results": results,
            "recommendation": self._generate_recommendation(sorted_results)
        }
    
    def iterate(self, original: str, improved: str) -> dict:
        """
        Compare original vs improved version.
        Shows delta for each dimension.
        """
        orig_result = self.evaluator.evaluate(original)
        new_result = self.evaluator.evaluate(improved)
        
        return {
            "improved": new_result.overall_score > orig_result.overall_score,
            "original_score": orig_result.overall_score,
            "new_score": new_result.overall_score,
            "delta": round(new_result.overall_score - orig_result.overall_score, 1),
            "changes": {
                "clarity": round(new_result.clarity_score - orig_result.clarity_score, 1),
                "specificity": round(new_result.specificity_score - orig_result.specificity_score, 1),
                "structure": round(new_result.structure_score - orig_result.structure_score, 1),
                "completeness": round(new_result.completeness_score - orig_result.completeness_score, 1),
            },
            "remaining_issues": new_result.weaknesses,
            "next_steps": new_result.suggestions
        }
    
    def _generate_recommendation(self, sorted_results: list) -> str:
        """Generate actionable recommendation from comparison."""
        if len(sorted_results) < 2:
            return "Single prompt evaluated."
        
        best = sorted_results[0]
        second = sorted_results[1]
        
        if best["score"] - second["score"] < 5:
            return f"Close match. {best['label']} edges out slightly. Consider combining strengths."
        elif best["score"] >= 75:
            return f"{best['label']} is production-ready. Minor refinements possible."
        else:
            return f"{best['label']} wins but needs work. Focus on: {', '.join(best['weaknesses'][:2])}"
    
    def get_history(self) -> list[dict]:
        """Return evaluation history for this session."""
        return [
            {"label": label, "score": result.overall_score, "type": result.prompt_type}
            for label, result in self.history
        ]


def batch_evaluate(prompts: list[str]) -> list[dict]:
    """
    Evaluate multiple prompts independently.
    Returns list of results in same order.
    """
    evaluator = PromptEvaluator()
    return [evaluator.evaluate(p).to_dict() for p in prompts]


# CLI
if __name__ == "__main__":
    comparator = PromptComparator()
    
    prompt_v1 = "write code to analyze data"
    
    prompt_v2 = """
    Write a Python function that analyzes sales data from a CSV file.
    
    Requirements:
    - Input: path to CSV with columns [date, product, quantity, price]
    - Output: dict with total_revenue, top_product, daily_averages
    - Handle missing values gracefully
    
    Include docstring and type hints.
    """
    
    result = comparator.iterate(prompt_v1, prompt_v2)
    
    print("ITERATION ANALYSIS")
    print("=" * 40)
    print(f"Improved: {'YES' if result['improved'] else 'NO'}")
    print(f"Score: {result['original_score']} -> {result['new_score']} ({result['delta']:+})")
    print(f"\nDimension Changes:")
    for dim, change in result['changes'].items():
        arrow = "^" if change > 0 else "v" if change < 0 else "="
        print(f"  {dim}: {change:+} {arrow}")
    
    if result['remaining_issues']:
        print(f"\nStill needs:")
        for issue in result['remaining_issues']:
            print(f"  - {issue}")
