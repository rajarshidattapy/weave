Google ADK
AnakinScraper toolkit for Google ADK

Google ADK tools for web scraping, search, and research — powered by Anakin. Build AI agents with Gemini that can extract data from any website, perform intelligent web searches, and conduct deep autonomous research.

PyPI	pypi.org/project/anakin-adk
Source	GitHub
Type	Tool
Version	0.1.2
Tools	4
License	MIT
Requires	Python >=3.10
How it works
You register Anakin tools with your Google ADK agent. When a user asks something that requires web data, Gemini automatically selects the right tool, fills in the parameters, and returns the results — no manual configuration needed.

User → "What's on this page?" → Gemini agent → scrape_website → Anakin API → results → Gemini → response
Copy
The tools expose their parameter schemas to Gemini via ADK's tool protocol, so the model knows when to use the browser, which country to route through, and whether to extract structured JSON — all based on the conversation context and your agent's instructions.

Key features
Anti-detection — Proxy routing across 207 countries prevents blocking
Intelligent Caching — Up to 30x faster on repeated requests
AI Extraction — Convert any webpage into structured JSON
Browser Automation — Full headless Chrome support for SPAs and JS-heavy sites
Batch Processing — Scrape up to 10 URLs in a single request
Deep Research — Autonomous multi-stage research combining search, scraping, and AI synthesis
Setup
1. Get your API key
Sign up at anakin.io/signup
Go to your Dashboard
Copy your API key (starts with ask_)
2. Install the package
pip install anakin-adk
Copy
You also need the Anakin CLI installed and authenticated:

pip install anakin-cli
anakin login --api-key "ask_your-key-here"
Copy
Tools
Each tool is exposed to Gemini with a full parameter schema. The model decides which parameters to use based on the user's request and your agent instructions. You can guide tool behavior by including hints in your agent's instruction field (e.g., "always use the browser for JavaScript-heavy sites" or "route through UK proxies").

1. scrape_website
Scrape a single URL and return clean markdown or structured JSON.

Parameter	Type	Required	Default	Description
url	string	Yes	—	Target URL to scrape (HTTP/HTTPS)
country	string	No	us	Proxy location from 207 countries
use_browser	boolean	No	false	Enable headless Chrome for JavaScript-heavy sites
generate_json	boolean	No	false	Use AI to extract structured data
session_id	string	No	—	Browser session ID for authenticated pages
Response includes: Raw HTML, cleaned HTML, markdown conversion, structured JSON (if generate_json enabled), cache status, timing metrics.

2. batch_scrape
Scrape up to 10 URLs at once and return combined results.

Parameter	Type	Required	Default	Description
urls	string	Yes	—	Comma-separated list of URLs (1–10)
country	string	No	us	Proxy location from 207 countries
use_browser	boolean	No	false	Enable headless Chrome for JavaScript-heavy sites
generate_json	boolean	No	false	Use AI to extract structured data from each page
Response includes: Per-URL results with HTML, markdown, and optional structured JSON.

3. search_web
AI-powered web search returning results with citations. Results are returned immediately without polling.

Parameter	Type	Required	Default	Description
prompt	string	Yes	—	Search query or question
limit	number	No	5	Maximum results to return
Response includes: Array of results with URLs, titles, snippets, publication dates, last updated timestamps.

4. deep_research
Autonomous multi-stage research pipeline combining search, scraping, and AI synthesis. Takes 1–5 minutes.

Parameter	Type	Required	Description
prompt	string	Yes	Research question or topic
Response includes: Comprehensive AI-generated report, structured findings, citations with source URLs, scraped source data, processing metrics.

Processing times
Tool	Type	Typical Duration
scrape_website	Async	3–15 seconds
batch_scrape	Async	5–30 seconds
search_web	Sync	Immediate
deep_research	Async	1–5 minutes
Usage
Full toolkit
Pass all 4 tools to your agent at once:

from anakin_adk import AnakinToolkit
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="web_researcher",
    instruction="Help users extract data from the web",
    tools=AnakinToolkit().get_tools(),
)
Copy
Run with the ADK dev UI:

adk web
Copy
Individual tools
Use specific tools instead of the full toolkit:

from anakin_adk import ScrapeWebsiteTool, SearchWebTool
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="search_and_scrape",
    instruction="Search the web and scrape relevant pages",
    tools=[SearchWebTool(), ScrapeWebsiteTool()],
)
Copy
Product research agent
An agent that compares products by scraping multiple pages:

from anakin_adk import AnakinToolkit
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="product_researcher",
    instruction="""You are a product research assistant.
When asked to compare products:
1. Use search_web to find relevant product pages
2. Use batch_scrape with generate_json=true to extract structured data
3. Summarize findings in a comparison table""",
    tools=AnakinToolkit().get_tools(),
)
Copy
Deep research agent
An agent for comprehensive research reports:

from anakin_adk import DeepResearchTool
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="deep_researcher",
    instruction="""You are a research analyst.
Use deep_research for broad questions that need multiple sources.
Use search_web + scrape_website for targeted fact-checking.""",
    tools=AnakinToolkit().get_tools(),
)
Copy
Geo-targeted scraping agent
An agent that routes through specific country proxies:

from anakin_adk import AnakinToolkit
from google.adk.agents import Agent

agent = Agent(
    model="gemini-2.5-pro",
    name="geo_scraper",
    instruction="""You scrape websites for users.
Always ask which country to route through.
Use use_browser=true for JavaScript-heavy sites.
Use generate_json=true when the user wants structured data.""",
    tools=AnakinToolkit().get_tools(),
)
Copy
More examples
The examples directory includes:

basic_scraping.py — Simple scrape agent
research_agent.py — Deep research agent
search_and_scrape.py — Multi-step: search then scrape
Troubleshooting
Code	Meaning	Action
400	Invalid parameters	Check your agent's instructions — Gemini may be passing unexpected values
401	Invalid API key	Run anakin login to re-authenticate
402	Plan upgrade required	Upgrade at Pricing
404	Job not found	Job may have expired
429	Rate limit exceeded	Reduce request frequency or upgrade your plan
5xx	Server error	Retry with backoff
Common issues:

Issue	Fix
Agent never uses tools	Check that tools= is set correctly and the instruction mentions web tasks
Empty scrape results	Add use_browser=true hint to your agent instruction for JS-heavy sites
Wrong country data	Add a country hint to your instruction (e.g., "always route through gb")
CLI not authenticated	Run anakin status to check, then anakin login if needed


