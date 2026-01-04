"""
Prompt Router with Integrated Evaluation
Routes prompts to appropriate handlers based on type and quality.
Can auto-enhance low-quality prompts before execution.
"""

from dataclasses import dataclass
from typing import Callable, Optional, Any
from enum import Enum
import json

from prompt_evaluator import PromptEvaluator, PromptType, EvaluationResult


class RouteAction(Enum):
    EXECUTE = "execute"           # Send to handler as-is
    ENHANCE = "enhance"           # Auto-improve then execute
    CLARIFY = "clarify"           # Request user clarification
    REJECT = "reject"             # Too low quality / risky


@dataclass
class RouteDecision:
    action: RouteAction
    handler_name: str
    original_prompt: str
    enhanced_prompt: Optional[str]
    evaluation: EvaluationResult
    reason: str


class PromptRouter:
    """
    Routes prompts based on evaluation scores and type detection.
    Integrates with MCP tools or custom handlers.
    """

    # Quality thresholds
    EXECUTE_THRESHOLD = 60      # Execute directly if score >= this
    ENHANCE_THRESHOLD = 35      # Auto-enhance if score >= this
    REJECT_THRESHOLD = 20       # Reject if score < this

    def __init__(self):
        self.evaluator = PromptEvaluator()
        self.handlers: dict[str, Callable] = {}
        self.type_mappings: dict[PromptType, str] = {}
        self.enhancement_templates: dict[PromptType, str] = {}
        self._setup_defaults()

    def _setup_defaults(self):
        """Configure default type-to-handler mappings."""
        self.type_mappings = {
            PromptType.CODE: "code_handler",
            PromptType.ANALYTICAL: "analysis_handler",
            PromptType.CREATIVE: "creative_handler",
            PromptType.SYSTEM: "system_handler",
            PromptType.INSTRUCTION: "instruction_handler",
            PromptType.CONVERSATIONAL: "chat_handler",
            PromptType.UNKNOWN: "default_handler",
        }

        # Templates to enhance weak prompts
        self.enhancement_templates = {
            PromptType.CODE: """
Task: {original}

Requirements:
- Language: Python (unless specified otherwise)
- Include error handling
- Add type hints and docstring
- Provide example usage

Output format: Complete, runnable code block.
""",
            PromptType.ANALYTICAL: """
Analysis Request: {original}

Please provide:
1. Key findings summary
2. Supporting data/evidence
3. Limitations or caveats
4. Recommendations

Format: Structured markdown with clear sections.
""",
            PromptType.CREATIVE: """
Creative task: {original}

Guidelines:
- Tone: Engaging and appropriate for audience
- Length: Moderate unless specified
- Include vivid details

Output: Complete creative piece.
""",
            PromptType.INSTRUCTION: """
{original}

Please explain step-by-step:
1. Prerequisites or context needed
2. Detailed instructions
3. Common pitfalls to avoid
4. Verification/success criteria
""",
        }

    def register_handler(self, name: str, handler: Callable):
        """Register a handler function for a route."""
        self.handlers[name] = handler

    def map_type_to_handler(self, prompt_type: PromptType, handler_name: str):
        """Override default type-to-handler mapping."""
        self.type_mappings[prompt_type] = handler_name

    def route(self, prompt: str, force_enhance: bool = False) -> RouteDecision:
        """
        Evaluate and route a prompt.
        
        Args:
            prompt: The input prompt
            force_enhance: Always enhance regardless of score
            
        Returns:
            RouteDecision with action, handler, and optional enhanced prompt
        """
        evaluation = self.evaluator.evaluate(prompt)
        prompt_type = PromptType(evaluation.prompt_type)
        handler_name = self.type_mappings.get(prompt_type, "default_handler")

        # Determine action based on score
        score = evaluation.overall_score

        if evaluation.risk_flags and any("LONG" not in r for r in evaluation.risk_flags):
            # Has non-length risk flags
            action = RouteAction.CLARIFY
            reason = f"Risk flags detected: {', '.join(evaluation.risk_flags)}"
            enhanced = None

        elif score >= self.EXECUTE_THRESHOLD and not force_enhance:
            action = RouteAction.EXECUTE
            reason = f"Score {score} meets threshold ({self.EXECUTE_THRESHOLD})"
            enhanced = None

        elif score >= self.ENHANCE_THRESHOLD or force_enhance:
            action = RouteAction.ENHANCE
            enhanced = self._enhance_prompt(prompt, prompt_type)
            reason = f"Score {score} below threshold, auto-enhanced"

        elif score < self.REJECT_THRESHOLD:
            action = RouteAction.REJECT
            reason = f"Score {score} too low. Issues: {', '.join(evaluation.weaknesses[:2])}"
            enhanced = None

        else:
            action = RouteAction.CLARIFY
            reason = f"Score {score} ambiguous. Need: {', '.join(evaluation.suggestions[:2])}"
            enhanced = None

        return RouteDecision(
            action=action,
            handler_name=handler_name,
            original_prompt=prompt,
            enhanced_prompt=enhanced,
            evaluation=evaluation,
            reason=reason
        )

    def _enhance_prompt(self, prompt: str, prompt_type: PromptType) -> str:
        """Apply enhancement template to weak prompt."""
        template = self.enhancement_templates.get(
            prompt_type,
            "Task: {original}\n\nPlease be specific and thorough in your response."
        )
        return template.format(original=prompt.strip())

    def execute(self, prompt: str, force_enhance: bool = False) -> dict:
        """
        Full pipeline: evaluate, route, and execute.
        
        Returns dict with decision info and handler result (if executed).
        """
        decision = self.route(prompt, force_enhance)

        result = {
            "action": decision.action.value,
            "handler": decision.handler_name,
            "reason": decision.reason,
            "score": decision.evaluation.overall_score,
            "type": decision.evaluation.prompt_type,
            "enhanced_prompt": decision.enhanced_prompt,
            "handler_result": None
        }

        if decision.action in [RouteAction.EXECUTE, RouteAction.ENHANCE]:
            handler = self.handlers.get(decision.handler_name)
            if handler:
                prompt_to_use = decision.enhanced_prompt or decision.original_prompt
                try:
                    result["handler_result"] = handler(prompt_to_use)
                except Exception as e:
                    result["handler_error"] = str(e)
            else:
                result["handler_error"] = f"No handler registered for '{decision.handler_name}'"

        return result

    def get_routing_summary(self, prompt: str) -> str:
        """Human-readable routing decision."""
        decision = self.route(prompt)
        
        lines = [
            f"Action: {decision.action.value.upper()}",
            f"Handler: {decision.handler_name}",
            f"Score: {decision.evaluation.overall_score}/100",
            f"Type: {decision.evaluation.prompt_type}",
            f"Reason: {decision.reason}",
        ]
        
        if decision.enhanced_prompt:
            lines.append(f"\nEnhanced prompt preview:")
            lines.append(decision.enhanced_prompt[:200] + "..." if len(decision.enhanced_prompt) > 200 else decision.enhanced_prompt)
        
        return "\n".join(lines)


# MCP Integration
ROUTER_TOOL_DEFINITION = {
    "name": "route_prompt",
    "description": "Evaluates a prompt and determines optimal routing (execute, enhance, clarify, or reject). Can auto-enhance weak prompts.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The prompt to route"
            },
            "force_enhance": {
                "type": "boolean",
                "description": "Force enhancement regardless of score",
                "default": False
            },
            "execute": {
                "type": "boolean",
                "description": "Execute the handler if routable",
                "default": False
            }
        },
        "required": ["prompt"]
    }
}


# Singleton router instance
_router_instance: Optional[PromptRouter] = None


def get_router() -> PromptRouter:
    """Get or create the singleton router."""
    global _router_instance
    if _router_instance is None:
        _router_instance = PromptRouter()
    return _router_instance


def handle_route_tool(arguments: dict) -> dict:
    """MCP tool handler for routing."""
    router = get_router()
    prompt = arguments.get("prompt", "")
    force_enhance = arguments.get("force_enhance", False)
    should_execute = arguments.get("execute", False)

    if not prompt.strip():
        return {"error": "Empty prompt"}

    if should_execute:
        return router.execute(prompt, force_enhance)
    else:
        decision = router.route(prompt, force_enhance)
        return {
            "action": decision.action.value,
            "handler": decision.handler_name,
            "score": decision.evaluation.overall_score,
            "type": decision.evaluation.prompt_type,
            "reason": decision.reason,
            "enhanced_prompt": decision.enhanced_prompt,
            "suggestions": decision.evaluation.suggestions
        }


# CLI Demo
if __name__ == "__main__":
    router = PromptRouter()

    # Register sample handlers
    router.register_handler("code_handler", lambda p: {"status": "code executed", "prompt_length": len(p)})
    router.register_handler("analysis_handler", lambda p: {"status": "analysis complete"})
    router.register_handler("default_handler", lambda p: {"status": "processed"})

    test_prompts = [
        "write code",  # Low quality - should enhance
        "Analyze Q3 revenue trends and identify top 3 growth drivers with supporting data",  # Good - execute
        "maybe do something with the stuff idk",  # Very low - reject/clarify
    ]

    for prompt in test_prompts:
        print("=" * 60)
        print(f"INPUT: {prompt[:50]}...")
        print("-" * 60)
        print(router.get_routing_summary(prompt))
        print()
