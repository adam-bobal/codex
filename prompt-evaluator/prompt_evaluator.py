"""
Prompt Evaluation Agent
Analyzes prompts for quality, clarity, and effectiveness.
Designed for integration with MCP servers or standalone use.
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class PromptType(Enum):
    INSTRUCTION = "instruction"
    CONVERSATIONAL = "conversational"
    SYSTEM = "system"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass
class EvaluationResult:
    overall_score: float  # 0-100
    clarity_score: float
    specificity_score: float
    structure_score: float
    completeness_score: float
    prompt_type: str
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    token_estimate: int
    risk_flags: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class PromptEvaluator:
    """
    Evaluates prompts across multiple dimensions.
    Can be used standalone or wrapped as MCP tool.
    """

    # Indicators for different prompt types
    TYPE_INDICATORS = {
        PromptType.SYSTEM: ["you are", "your role", "act as", "behave as", "system:"],
        PromptType.CODE: ["write code", "function", "script", "debug", "implement", "```"],
        PromptType.ANALYTICAL: ["analyze", "evaluate", "compare", "assess", "review"],
        PromptType.CREATIVE: ["write a story", "create", "imagine", "generate", "compose"],
        PromptType.INSTRUCTION: ["step by step", "how to", "explain", "list", "describe"],
    }

    # Quality indicators
    CLARITY_MARKERS = [
        "specifically", "exactly", "must", "should", "format", "output",
        "return", "include", "exclude", "avoid"
    ]

    VAGUE_MARKERS = [
        "maybe", "perhaps", "something like", "kind of", "sort of",
        "etc", "and so on", "whatever", "stuff"
    ]

    STRUCTURE_MARKERS = [
        "##", "- ", "1.", "2.", "step", "first", "then", "finally",
        "input:", "output:", "context:", "task:"
    ]

    def __init__(self):
        self.last_result: Optional[EvaluationResult] = None

    def evaluate(self, prompt: str) -> EvaluationResult:
        """Main evaluation method."""
        prompt_lower = prompt.lower()

        # Detect prompt type
        prompt_type = self._detect_type(prompt_lower)

        # Calculate individual scores
        clarity = self._score_clarity(prompt, prompt_lower)
        specificity = self._score_specificity(prompt, prompt_lower)
        structure = self._score_structure(prompt)
        completeness = self._score_completeness(prompt, prompt_lower, prompt_type)

        # Calculate overall (weighted)
        overall = (
            clarity * 0.25 +
            specificity * 0.30 +
            structure * 0.20 +
            completeness * 0.25
        )

        # Generate feedback
        strengths = self._identify_strengths(prompt, clarity, specificity, structure)
        weaknesses = self._identify_weaknesses(prompt, prompt_lower, clarity, specificity)
        suggestions = self._generate_suggestions(prompt, prompt_lower, prompt_type, weaknesses)
        risk_flags = self._check_risks(prompt, prompt_lower)

        # Token estimate (rough: ~4 chars per token)
        token_estimate = len(prompt) // 4

        result = EvaluationResult(
            overall_score=round(overall, 1),
            clarity_score=round(clarity, 1),
            specificity_score=round(specificity, 1),
            structure_score=round(structure, 1),
            completeness_score=round(completeness, 1),
            prompt_type=prompt_type.value,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            token_estimate=token_estimate,
            risk_flags=risk_flags
        )

        self.last_result = result
        return result

    def _detect_type(self, prompt_lower: str) -> PromptType:
        """Classify the prompt type."""
        scores = {}
        for ptype, indicators in self.TYPE_INDICATORS.items():
            scores[ptype] = sum(1 for ind in indicators if ind in prompt_lower)

        if max(scores.values()) == 0:
            return PromptType.CONVERSATIONAL

        return max(scores, key=scores.get)

    def _score_clarity(self, prompt: str, prompt_lower: str) -> float:
        """Score how clear the prompt is."""
        score = 50.0  # baseline

        # Positive: clarity markers
        clarity_count = sum(1 for m in self.CLARITY_MARKERS if m in prompt_lower)
        score += min(clarity_count * 5, 25)

        # Negative: vague language
        vague_count = sum(1 for m in self.VAGUE_MARKERS if m in prompt_lower)
        score -= vague_count * 8

        # Positive: reasonable sentence length (not too long)
        sentences = re.split(r'[.!?]', prompt)
        avg_words = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if 10 <= avg_words <= 25:
            score += 10
        elif avg_words > 40:
            score -= 15

        return max(0, min(100, score))

    def _score_specificity(self, prompt: str, prompt_lower: str) -> float:
        """Score how specific the prompt is."""
        score = 40.0

        # Check for concrete requirements
        if re.search(r'\d+', prompt):  # numbers
            score += 10
        if re.search(r'"[^"]+"|\'[^\']+\'', prompt):  # quoted examples
            score += 15
        if "example" in prompt_lower or "e.g." in prompt_lower:
            score += 10
        if re.search(r'format|output|return', prompt_lower):
            score += 10
        if re.search(r'do not|don\'t|avoid|never', prompt_lower):
            score += 8  # constraints specified

        # Length bonus (longer usually more specific, to a point)
        word_count = len(prompt.split())
        if 50 <= word_count <= 300:
            score += 15
        elif word_count < 20:
            score -= 20

        return max(0, min(100, score))

    def _score_structure(self, prompt: str) -> float:
        """Score the structural organization."""
        score = 40.0

        # Check for markdown/structure
        structure_count = sum(1 for m in self.STRUCTURE_MARKERS if m in prompt)
        score += min(structure_count * 8, 30)

        # Line breaks indicate organization
        line_count = prompt.count('\n')
        if 3 <= line_count <= 15:
            score += 15
        elif line_count > 20:
            score += 10  # organized but maybe verbose

        # XML tags (common in system prompts)
        if re.search(r'<[a-z_]+>', prompt.lower()):
            score += 15

        return max(0, min(100, score))

    def _score_completeness(self, prompt: str, prompt_lower: str, ptype: PromptType) -> float:
        """Score completeness based on prompt type."""
        score = 50.0

        # Universal checks
        if "context" in prompt_lower or "background" in prompt_lower:
            score += 10

        # Type-specific
        if ptype == PromptType.CODE:
            if "language" in prompt_lower or "python" in prompt_lower or "javascript" in prompt_lower:
                score += 10
            if "error" in prompt_lower or "input" in prompt_lower:
                score += 10

        elif ptype == PromptType.ANALYTICAL:
            if "criteria" in prompt_lower or "metrics" in prompt_lower:
                score += 15
            if "data" in prompt_lower or "source" in prompt_lower:
                score += 10

        elif ptype == PromptType.SYSTEM:
            if "tone" in prompt_lower or "style" in prompt_lower:
                score += 10
            if "constraint" in prompt_lower or "limitation" in prompt_lower:
                score += 10

        # Has clear task/goal
        if re.search(r'task:|goal:|objective:|purpose:', prompt_lower):
            score += 15

        return max(0, min(100, score))

    def _identify_strengths(self, prompt: str, clarity: float, specificity: float, structure: float) -> list[str]:
        """List what the prompt does well."""
        strengths = []

        if clarity >= 70:
            strengths.append("Clear and unambiguous language")
        if specificity >= 70:
            strengths.append("Good level of detail and specificity")
        if structure >= 70:
            strengths.append("Well-organized structure")
        if len(prompt.split()) >= 50:
            strengths.append("Sufficient context provided")
        if re.search(r'"[^"]+"|\'[^\']+\'', prompt):
            strengths.append("Includes concrete examples")
        if re.search(r'do not|don\'t|avoid', prompt.lower()):
            strengths.append("Defines negative constraints")

        return strengths if strengths else ["Basic prompt structure present"]

    def _identify_weaknesses(self, prompt: str, prompt_lower: str, clarity: float, specificity: float) -> list[str]:
        """List areas for improvement."""
        weaknesses = []

        if clarity < 50:
            weaknesses.append("Language is vague or ambiguous")
        if specificity < 50:
            weaknesses.append("Lacks specific requirements or constraints")
        if len(prompt.split()) < 20:
            weaknesses.append("Too brief - may produce inconsistent results")
        if not re.search(r'format|output|return', prompt_lower):
            weaknesses.append("No output format specified")

        vague_found = [m for m in self.VAGUE_MARKERS if m in prompt_lower]
        if vague_found:
            weaknesses.append(f"Contains vague terms: {', '.join(vague_found[:3])}")

        return weaknesses

    def _generate_suggestions(self, prompt: str, prompt_lower: str, ptype: PromptType, weaknesses: list) -> list[str]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        if "No output format specified" in weaknesses:
            suggestions.append("Add: 'Return your response as [JSON/markdown/bullet points]'")

        if "Too brief" in weaknesses:
            suggestions.append("Expand with context, examples, and constraints")

        if ptype == PromptType.CODE and "test" not in prompt_lower:
            suggestions.append("Consider adding: 'Include example usage or tests'")

        if ptype == PromptType.ANALYTICAL and "criteria" not in prompt_lower:
            suggestions.append("Specify evaluation criteria or metrics")

        if not re.search(r'<[a-z_]+>', prompt_lower) and len(prompt) > 200:
            suggestions.append("Consider using XML tags to separate sections")

        if "step" not in prompt_lower and ptype in [PromptType.INSTRUCTION, PromptType.CODE]:
            suggestions.append("Add: 'Think step by step' for complex tasks")

        return suggestions if suggestions else ["Prompt is reasonably complete"]

    def _check_risks(self, prompt: str, prompt_lower: str) -> list[str]:
        """Flag potential issues."""
        risks = []

        if len(prompt) > 4000:
            risks.append("LONG: May hit token limits or reduce response quality")

        if prompt_lower.count("do not") > 3 or prompt_lower.count("don't") > 3:
            risks.append("NEGATIVE_HEAVY: Too many negative constraints can confuse")

        if re.search(r'always|never|must always|must never', prompt_lower):
            risks.append("ABSOLUTE: Absolute terms may cause rigid behavior")

        if prompt.count('\n\n\n') > 2:
            risks.append("FORMATTING: Excessive whitespace")

        return risks


def evaluate_prompt(prompt: str) -> dict:
    """
    Standalone function for easy import/MCP integration.
    Returns dict with all evaluation results.
    """
    evaluator = PromptEvaluator()
    result = evaluator.evaluate(prompt)
    return result.to_dict()


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            test_prompt = f.read()
    else:
        # Example prompt for testing
        test_prompt = """
        You are a financial analyst assistant. Analyze the provided quarterly report 
        and identify key trends in revenue and expenses. 
        
        Format your response as:
        1. Executive Summary (2-3 sentences)
        2. Revenue Analysis
        3. Expense Analysis  
        4. Recommendations
        
        Be specific and cite numbers from the report.
        """

    evaluator = PromptEvaluator()
    result = evaluator.evaluate(test_prompt)

    print("=" * 60)
    print("PROMPT EVALUATION REPORT")
    print("=" * 60)
    print(f"\nOverall Score: {result.overall_score}/100")
    print(f"Prompt Type: {result.prompt_type}")
    print(f"Est. Tokens: {result.token_estimate}")
    print(f"\nScores:")
    print(f"  Clarity:      {result.clarity_score}/100")
    print(f"  Specificity:  {result.specificity_score}/100")
    print(f"  Structure:    {result.structure_score}/100")
    print(f"  Completeness: {result.completeness_score}/100")
    print(f"\nStrengths:")
    for s in result.strengths:
        print(f"  + {s}")
    print(f"\nWeaknesses:")
    for w in result.weaknesses:
        print(f"  - {w}")
    print(f"\nSuggestions:")
    for s in result.suggestions:
        print(f"  > {s}")
    if result.risk_flags:
        print(f"\nRisk Flags:")
        for r in result.risk_flags:
            print(f"  ! {r}")
