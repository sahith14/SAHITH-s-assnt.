"""
Web tools — search, fetch pages, and global news briefings.
"""

import httpx
import xml.etree.ElementTree as ET
import asyncio
import re
import webbrowser

SEED_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://www.cnbc.com/id/100727362/device/rss/rss.html',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.aljazeera.com/xml/rss/all.xml'
]

async def fetch_and_parse_feed(client, url):
    """Helper function to handle a single feed request and parse its XML."""
    try:
        response = await client.get(url, headers={'User-Agent': 'Friday-AI/1.0'}, timeout=5.0)
        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        source_name = url.split('.')[1].upper() if '.' in url else "NEWS"
        
        feed_items = []
        items = root.findall(".//item")[:5]
        for item in items:
            title = item.findtext("title")
            description = item.findtext("description")
            link = item.findtext("link")
            
            if description:
                description = re.sub('<[^<]+?>', '', description).strip()

            feed_items.append({
                "source": source_name,
                "title": title,
                "summary": description[:200] + "..." if description else "",
                "link": link
            })
        return feed_items
    except Exception as e:
        return []

async def get_world_news() -> str:
    """Fetches the latest global headlines from major news outlets."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        tasks = [fetch_and_parse_feed(client, url) for url in SEED_FEEDS]
        results_of_lists = await asyncio.gather(*tasks)
        all_articles = [item for sublist in results_of_lists for item in sublist]

    if not all_articles:
        return "The global news grid is unresponsive, sir."

    report = []
    for entry in all_articles[:12]:
        report.append(f"• [{entry['source']}] {entry['title']}")
        if entry['summary']:
            report.append(f"  {entry['summary']}")

    return "\n".join(report)

async def search_web(query: str) -> str:
    """Search the web for a given query."""
    return f"Search results for: {query} (search API not configured)"

async def fetch_url(url: str) -> str:
    """Fetch the raw text content of a URL."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text[:4000]

async def open_world_monitor() -> str:
    """Opens the World Monitor dashboard in browser."""
    url = "https://worldmonitor.app/"
    try:
        webbrowser.open(url)
        return "Displaying the World Monitor on your primary screen now, sir."
    except Exception as e:
        return f"I'm unable to initialize the visual monitor: {str(e)}"

def register(mcp):
    """Register tools with MCP server (if using FastMCP)"""
    @mcp.tool()
    async def get_world_news_tool() -> str:
        return await get_world_news()

    @mcp.tool()
    async def search_web_tool(query: str) -> str:
        return await search_web(query)

    @mcp.tool()
    async def fetch_url_tool(url: str) -> str:
        return await fetch_url(url)

    @mcp.tool()
    async def open_world_monitor_tool() -> str:
        return await open_world_monitor()
