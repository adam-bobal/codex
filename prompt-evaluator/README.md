# Prompt Evaluator Agent

Analyzes prompts for quality, providing scores, weaknesses, and actionable suggestions.

## Evaluation Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| Clarity | 25% | Unambiguous language, no vague terms |
| Specificity | 30% | Concrete requirements, examples, constraints |
| Structure | 20% | Organization, formatting, logical flow |
| Completeness | 25% | All necessary info for task type |

## Usage

### Standalone
```python
from prompt_evaluator import evaluate_prompt

result = evaluate_prompt("Your prompt here")
print(result["overall_score"])  # 0-100
print(result["suggestions"])    # List of improvements
```

### CLI
```bash
python prompt_evaluator.py                    # Run with example
python prompt_evaluator.py my_prompt.txt      # Evaluate file
```

### MCP Integration
```python
from mcp_tool import TOOL_DEFINITION, handle_tool_call

# Register TOOL_DEFINITION with your MCP server
# Call handle_tool_call({"prompt": "..."}) on tool invocation
```

### Compare Prompts
```python
from comparator import PromptComparator

comp = PromptComparator()
result = comp.compare([prompt_a, prompt_b], ["Version A", "Version B"])
print(result["winner"])
```

## Output Example

```
Score: 72/100 (analytical)
Tokens: ~85

Breakdown:
  Clarity: 75 | Specificity: 68
  Structure: 80 | Completeness: 65

Fix:
  - No output format specified

Try:
  > Add: 'Return your response as [JSON/markdown/bullet points]'
  > Specify evaluation criteria or metrics
```

## Risk Flags

- `LONG` - May hit token limits
- `NEGATIVE_HEAVY` - Too many "do not" constraints
- `ABSOLUTE` - Rigid always/never terms
