# MCP Server Structure for Google AdWords Agent

## Tool Architecture

```
google-ads-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── reporting.py    # Read-only metrics tools
│   │   ├── campaigns.py    # Campaign management tools
│   │   └── bidding.py      # Bid adjustment tools
│   ├── auth/
│   │   ├── __init__.py
│   │   └── oauth.py        # OAuth2 credential management
│   └── utils/
│       ├── __init__.py
│       └── formatters.py   # Response formatting
├── config/
│   └── google-ads.yaml     # Credentials (git-ignored)
├── requirements.txt
└── README.md
```

## MCP Tool Definitions

### Reporting Tools (Phase 1)

```python
# tools/reporting.py

@mcp_tool(
    name="get_campaign_performance",
    description="Retrieve performance metrics for campaigns over a date range"
)
async def get_campaign_performance(
    customer_id: str,
    start_date: str,  # YYYY-MM-DD
    end_date: str,
    metrics: list[str] = ["clicks", "impressions", "cost_micros", "conversions"]
) -> dict:
    """Returns campaign-level performance data."""
    pass

@mcp_tool(
    name="get_daily_spend_summary",
    description="Get total spend across all campaigns for today/yesterday"
)
async def get_daily_spend_summary(
    customer_id: str,
    date: str = "TODAY"  # TODAY, YESTERDAY, or YYYY-MM-DD
) -> dict:
    pass

@mcp_tool(
    name="detect_anomalies",
    description="Identify campaigns with unusual performance changes"
)
async def detect_anomalies(
    customer_id: str,
    threshold_pct: float = 20.0,  # % change to flag
    lookback_days: int = 7
) -> list[dict]:
    pass
```

### Campaign Management Tools (Phase 2)

```python
# tools/campaigns.py

@mcp_tool(
    name="list_campaigns",
    description="List all campaigns with status and budget info"
)
async def list_campaigns(
    customer_id: str,
    status_filter: str = "ENABLED"  # ENABLED, PAUSED, ALL
) -> list[dict]:
    pass

@mcp_tool(
    name="pause_campaign",
    description="Pause a campaign by ID"
)
async def pause_campaign(
    customer_id: str,
    campaign_id: str
) -> dict:
    pass

@mcp_tool(
    name="update_budget",
    description="Update daily budget for a campaign"
)
async def update_budget(
    customer_id: str,
    campaign_id: str,
    new_budget_micros: int  # Budget in micros (1,000,000 = $1)
) -> dict:
    pass
```

### Bidding Tools (Phase 3)

```python
# tools/bidding.py

@mcp_tool(
    name="adjust_keyword_bids",
    description="Adjust CPC bids for keywords based on performance"
)
async def adjust_keyword_bids(
    customer_id: str,
    campaign_id: str,
    adjustment_rules: dict  # e.g., {"ctr_below": 1.0, "action": "decrease_10pct"}
) -> list[dict]:
    pass

@mcp_tool(
    name="get_bid_recommendations",
    description="Get AI-suggested bid adjustments based on performance"
)
async def get_bid_recommendations(
    customer_id: str,
    campaign_id: str,
    target_metric: str = "conversions"  # conversions, clicks, impression_share
) -> list[dict]:
    pass
```

## Server Entry Point

```python
# server.py

from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("google-ads-agent")

# Register tools from each module
from tools.reporting import *
from tools.campaigns import *
from tools.bidding import *

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "python",
      "args": ["-m", "google_ads_mcp.server"],
      "cwd": "C:\\environments\\projects\\marketing\\google-adwords-agent"
    }
  }
}
```

## Security Considerations

1. Never log full credentials
2. Use environment variables for secrets in production
3. Implement rate limiting (Google Ads API has quotas)
4. Add confirmation prompts for write operations
