"""
MCP Tool Wrapper for Prompt Evaluator
Drop-in integration for MCP server workflows.
"""

from prompt_evaluator import evaluate_prompt, PromptEvaluator


# MCP Tool Definition (for server registration)
TOOL_DEFINITION = {
    "name": "evaluate_prompt",
    "description": "Evaluates a prompt for quality, clarity, specificity, and structure. Returns scores and improvement suggestions.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt text to evaluate"
            },
            "verbose": {
                "type": "boolean",
                "description": "Include detailed breakdown",
                "default": True
            }
        },
        "required": ["prompt"]
    }
}


def handle_tool_call(arguments: dict) -> dict:
    """
    MCP tool handler function.
    
    Args:
        arguments: Dict with 'prompt' and optional 'verbose'
    
    Returns:
        Evaluation results as dict
    """
    prompt = arguments.get("prompt", "")
    verbose = arguments.get("verbose", True)
    
    if not prompt.strip():
        return {
            "error": "Empty prompt provided",
            "overall_score": 0
        }
    
    result = evaluate_prompt(prompt)
    
    if not verbose:
        # Return condensed version
        return {
            "overall_score": result["overall_score"],
            "prompt_type": result["prompt_type"],
            "top_suggestion": result["suggestions"][0] if result["suggestions"] else None,
            "risk_flags": result["risk_flags"]
        }
    
    return result


def format_for_display(result: dict) -> str:
    """Format evaluation result for human-readable output."""
    lines = [
        f"Score: {result['overall_score']}/100 ({result['prompt_type']})",
        f"Tokens: ~{result['token_estimate']}",
        "",
        "Breakdown:",
        f"  Clarity: {result['clarity_score']} | Specificity: {result['specificity_score']}",
        f"  Structure: {result['structure_score']} | Completeness: {result['completeness_score']}",
    ]
    
    if result['weaknesses']:
        lines.append("\nFix:")
        for w in result['weaknesses'][:2]:
            lines.append(f"  - {w}")
    
    if result['suggestions']:
        lines.append("\nTry:")
        for s in result['suggestions'][:2]:
            lines.append(f"  > {s}")
    
    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    test = {
        "prompt": "write me some code",
        "verbose": True
    }
    
    result = handle_tool_call(test)
    print(format_for_display(result))
