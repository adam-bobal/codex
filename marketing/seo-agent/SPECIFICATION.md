# SEO Agent - Technical Specification

## Target APIs Analysis

### Tier 1: Free/Owned Data (Recommended Start)

| API | Cost | Data Type | Auth |
|-----|------|-----------|------|
| **Google Search Console** | Free | Rankings, clicks, impressions, crawl errors | OAuth2 |
| **Google Analytics 4** | Free | Traffic, conversions, user behavior | OAuth2 |
| **Bing Webmaster Tools** | Free | Rankings for Bing ecosystem | OAuth2 |

### Tier 2: Freemium APIs

| API | Free Tier | Paid | Data Type |
|-----|-----------|------|-----------|
| **Serpstat** | 30 queries/day | $69/mo | Keywords, backlinks, competitors |
| **DataForSEO** | $50 credit | Pay-per-use | SERP, keywords, backlinks |
| **Moz** | 10 queries/mo | $99/mo | DA/PA, backlinks |

### Tier 3: Premium APIs (Enterprise)

| API | Cost | Best For |
|-----|------|----------|
| **Ahrefs** | $99/mo+ | Backlink analysis, competitive research |
| **SEMrush** | $119/mo+ | All-in-one SEO toolkit |
| **Majestic** | $49/mo+ | Backlink index depth |

### Tier 4: Scrape-Based Alternatives (Zero Cost)

| Tool | Capability | Risk |
|------|------------|------|
| **SerpApi** | $50 free credit | SERP scraping abstraction |
| **Custom Playwright** | DIY SERP scraping | IP blocking, TOS violation |
| **Brightdata/Oxylabs** | Proxy + scraping | Costly at scale |

## Recommended Stack (Zero-Cost Priority)

```
Primary: Google Search Console API (free, official)
Secondary: Google Analytics 4 API (free, official)
Tertiary: DataForSEO free tier for competitive data
Fallback: Playwright scraping for spot checks
```

---

## Agent Actions Definition

### Core Actions (MCP Tools)

```python
# 1. KEYWORD TRACKING
@mcp_tool(name="track_keyword_rankings")
async def track_keyword_rankings(
    site_url: str,
    keywords: list[str],
    country: str = "usa",
    date_range: str = "28d"
) -> dict:
    """
    Track ranking positions for target keywords.
    Source: Google Search Console API
    Returns: position, impressions, clicks, CTR per keyword
    """

@mcp_tool(name="discover_keyword_opportunities") 
async def discover_keyword_opportunities(
    site_url: str,
    min_impressions: int = 100,
    max_position: float = 20.0
) -> list[dict]:
    """
    Find keywords ranking 11-20 (page 2) with high impressions.
    These are quick-win optimization targets.
    """

# 2. CONTENT SUGGESTIONS
@mcp_tool(name="analyze_content_gaps")
async def analyze_content_gaps(
    site_url: str,
    competitor_urls: list[str],
    topic_focus: str
) -> list[dict]:
    """
    Compare your content coverage vs competitors.
    Returns: missing topics, underperforming pages, expansion opportunities
    """

@mcp_tool(name="suggest_content_updates")
async def suggest_content_updates(
    page_url: str,
    target_keyword: str
) -> dict:
    """
    Analyze page vs top-ranking competitors.
    Returns: word count gap, missing subtopics, recommended additions
    """

@mcp_tool(name="generate_content_brief")
async def generate_content_brief(
    target_keyword: str,
    content_type: str = "blog"  # blog, landing, product
) -> dict:
    """
    Generate content brief based on SERP analysis.
    Returns: outline, word count target, key entities to include
    """

# 3. BACKLINK MONITORING
@mcp_tool(name="get_backlink_summary")
async def get_backlink_summary(
    site_url: str
) -> dict:
    """
    Get overview of backlink profile.
    Returns: total backlinks, referring domains, top anchors, new/lost
    """

@mcp_tool(name="monitor_new_backlinks")
async def monitor_new_backlinks(
    site_url: str,
    since_days: int = 7
) -> list[dict]:
    """
    Track newly acquired backlinks.
    Returns: source URL, anchor text, DA, first seen date
    """

@mcp_tool(name="find_broken_backlinks")
async def find_broken_backlinks(
    site_url: str
) -> list[dict]:
    """
    Find backlinks pointing to 404/broken pages.
    Returns: source URL, target URL, suggested redirect
    """

@mcp_tool(name="analyze_competitor_backlinks")
async def analyze_competitor_backlinks(
    competitor_url: str,
    min_domain_authority: int = 30
) -> list[dict]:
    """
    Find high-quality backlinks competitors have.
    Returns: linking domain, page, anchor, your status (have/missing)
    """

# 4. TECHNICAL SEO
@mcp_tool(name="check_crawl_errors")
async def check_crawl_errors(
    site_url: str
) -> dict:
    """
    Get crawl error summary from Search Console.
    Returns: 404s, 5xx errors, crawl anomalies
    """

@mcp_tool(name="analyze_core_web_vitals")
async def analyze_core_web_vitals(
    page_url: str
) -> dict:
    """
    Get CWV metrics (LCP, FID, CLS) for page.
    Source: CrUX API or PageSpeed Insights
    """

# 5. REPORTING
@mcp_tool(name="generate_seo_report")
async def generate_seo_report(
    site_url: str,
    report_type: str = "weekly",  # weekly, monthly, quarterly
    include_sections: list[str] = ["rankings", "traffic", "backlinks"]
) -> dict:
    """
    Generate comprehensive SEO performance report.
    Returns: structured data + optional markdown summary
    """
```

---

## Implementation Priority

| Phase | Actions | Data Source | Timeline |
|-------|---------|-------------|----------|
| **1** | Keyword tracking, crawl errors | GSC | Week 1 |
| **2** | Traffic analysis, CWV | GA4 + PageSpeed | Week 2 |
| **3** | Backlink monitoring | DataForSEO/Moz | Week 3 |
| **4** | Content suggestions | LLM + SERP data | Week 4 |
| **5** | Competitor analysis | DataForSEO | Week 5+ |

## Data Storage Schema

```sql
-- Core tables for SEO agent
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    site_url TEXT,
    keyword TEXT,
    current_position REAL,
    impressions INTEGER,
    clicks INTEGER,
    ctr REAL,
    date_checked DATE,
    UNIQUE(site_url, keyword, date_checked)
);

CREATE TABLE backlinks (
    id INTEGER PRIMARY KEY,
    target_site TEXT,
    source_url TEXT,
    anchor_text TEXT,
    domain_authority INTEGER,
    first_seen DATE,
    last_seen DATE,
    status TEXT  -- active, lost
);

CREATE TABLE content_pages (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    word_count INTEGER,
    target_keyword TEXT,
    last_updated DATE,
    performance_score REAL
);
```
