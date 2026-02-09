"""
Marketing Agent Pipeline - Custom Tools
========================================
Tools that agents use to interact with external services.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional

from crewai.tools import tool
from tavily import TavilyClient

from config import (
    TAVILY_API_KEY, SERPER_API_KEY, BUFFER_ACCESS_TOKEN,
    MAILERLITE_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
)


# =============================================================================
# SEARCH & RESEARCH TOOLS
# =============================================================================

@tool("Search Trends")
def search_trends(query: str) -> str:
    """Search for trending topics and current news using Tavily.
    Use this to find what's trending in your niche right now."""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_raw_content=False,
        )
        output = []
        for r in results.get("results", []):
            output.append(f"**{r.get('title', 'N/A')}**\n{r.get('content', '')[:300]}\nURL: {r.get('url', '')}\n")
        return "\n---\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {e}"


@tool("Google Search")
def google_search(query: str) -> str:
    """Search Google via Serper for forums, Reddit threads, and broad web content.
    Great for finding what real people are discussing."""
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": 10},
        )
        if response.status_code != 200:
            return f"Serper API error: {response.status_code}"

        data = response.json()
        output = []
        for item in data.get("organic", []):
            output.append(f"**{item.get('title', 'N/A')}**\n{item.get('snippet', '')}\nURL: {item.get('link', '')}\n")
        return "\n---\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {e}"


# =============================================================================
# SOCIAL MEDIA TOOLS
# =============================================================================

@tool("Post to Buffer")
def post_to_buffer(text: str, platform: str = "twitter") -> str:
    """Schedule a social media post via Buffer API.
    Platforms: twitter, instagram, linkedin, facebook."""
    if not BUFFER_ACCESS_TOKEN:
        return "Buffer API token not configured. Post saved locally instead."

    try:
        # Get profiles
        profiles_resp = requests.get(
            "https://api.bufferapp.com/1/profiles.json",
            params={"access_token": BUFFER_ACCESS_TOKEN},
        )
        profiles = profiles_resp.json()

        target_profile = None
        for p in profiles:
            if platform.lower() in p.get("service", "").lower():
                target_profile = p
                break

        if not target_profile:
            return f"No {platform} profile found in Buffer. Available: {[p.get('service') for p in profiles]}"

        # Create post
        resp = requests.post(
            "https://api.bufferapp.com/1/updates/create.json",
            data={
                "access_token": BUFFER_ACCESS_TOKEN,
                "profile_ids[]": target_profile["id"],
                "text": text,
                "now": False,  # Queue it
            },
        )
        result = resp.json()
        if result.get("success"):
            return f"Post queued on {platform} via Buffer! ID: {result.get('updates', [{}])[0].get('id', 'unknown')}"
        return f"Buffer error: {result.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Buffer API error: {e}"


@tool("Save Post Locally")
def save_post_locally(content: str, platform: str, post_type: str = "text") -> str:
    """Save generated post content to local file for manual review or later scheduling.
    Use this when API access is not available."""
    os.makedirs("output/posts", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"output/posts/{platform}-{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {platform.upper()} Post\n\n")
        f.write(f"**Type:** {post_type}\n")
        f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Platform:** {platform}\n\n---\n\n")
        f.write(content)

    return f"Post saved to {filename}"


# =============================================================================
# SEO TOOLS
# =============================================================================

@tool("Keyword Research")
def keyword_research(topic: str) -> str:
    """Find relevant long-tail keywords for a topic using Google search suggestions
    and related searches. Free alternative to paid keyword tools."""
    try:
        keywords = []

        # Google autocomplete
        resp = requests.get(
            "https://suggestqueries.google.com/complete/search",
            params={"client": "firefox", "q": topic},
        )
        if resp.status_code == 200:
            suggestions = resp.json()
            if len(suggestions) > 1:
                keywords.extend(suggestions[1][:10])

        # Serper related searches
        resp2 = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": topic, "num": 5},
        )
        if resp2.status_code == 200:
            data = resp2.json()
            for item in data.get("relatedSearches", []):
                keywords.append(item.get("query", ""))
            # People also ask
            for item in data.get("peopleAlsoAsk", []):
                keywords.append(item.get("question", ""))

        unique = list(dict.fromkeys(k for k in keywords if k))
        return f"Found {len(unique)} keywords for '{topic}':\n" + "\n".join(f"- {k}" for k in unique)
    except Exception as e:
        return f"Keyword research error: {e}"


@tool("Generate SEO Article")
def save_seo_article(title: str, content: str, keywords: str) -> str:
    """Save an SEO-optimized article to the output directory."""
    os.makedirs("output/articles", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:50]
    filename = f"output/articles/{safe_title}-{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: \"{title}\"\nkeywords: \"{keywords}\"\ndate: {datetime.now().isoformat()}\n---\n\n")
        f.write(content)

    return f"Article saved to {filename}"


# =============================================================================
# EMAIL TOOLS
# =============================================================================

@tool("Send Email via MailerLite")
def send_email_mailerlite(subject: str, content: str, group_id: Optional[str] = None) -> str:
    """Send an email campaign via MailerLite API.
    If group_id not provided, sends to all subscribers."""
    if not MAILERLITE_API_KEY:
        return "MailerLite API key not configured. Email saved locally instead."

    try:
        headers = {
            "Authorization": f"Bearer {MAILERLITE_API_KEY}",
            "Content-Type": "application/json",
        }

        # Create campaign
        campaign_data = {
            "name": f"Auto Campaign - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "type": "regular",
            "emails": [{
                "subject": subject,
                "from_name": "Marketing Bot",
                "content": content,
            }],
        }

        if group_id:
            campaign_data["groups"] = [group_id]

        resp = requests.post(
            "https://connect.mailerlite.com/api/campaigns",
            headers=headers,
            json=campaign_data,
        )

        if resp.status_code in (200, 201):
            return f"Email campaign created: {subject}"
        return f"MailerLite error: {resp.status_code} - {resp.text[:200]}"
    except Exception as e:
        return f"Email error: {e}"


@tool("Save Email Draft")
def save_email_draft(subject: str, content: str, sequence_position: int = 1) -> str:
    """Save an email draft locally for review before sending."""
    os.makedirs("output/emails", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"output/emails/seq{sequence_position:02d}-{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Email Draft\n\n")
        f.write(f"**Subject:** {subject}\n")
        f.write(f"**Sequence Position:** {sequence_position}\n")
        f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n")
        f.write(content)

    return f"Email draft saved to {filename}"


# =============================================================================
# NOTIFICATION TOOLS
# =============================================================================

@tool("Send Telegram Notification")
def send_telegram(message: str) -> str:
    """Send a notification message to the owner via Telegram bot.
    Use this for daily reports and important alerts."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return "Telegram not configured. Message logged instead."

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
        )
        if resp.status_code == 200:
            return "Telegram notification sent!"
        return f"Telegram error: {resp.text[:200]}"
    except Exception as e:
        return f"Telegram error: {e}"


# =============================================================================
# ANALYTICS TOOLS
# =============================================================================

@tool("Read Analytics Report")
def read_analytics(source: str = "all") -> str:
    """Read the latest analytics data from saved reports.
    Sources: posts, emails, seo, all"""
    os.makedirs("output/analytics", exist_ok=True)

    report_path = "output/analytics/latest_report.json"
    if not os.path.exists(report_path):
        return "No analytics data available yet. Run some campaigns first."

    with open(report_path, "r") as f:
        data = json.load(f)

    if source != "all" and source in data:
        return json.dumps(data[source], indent=2)
    return json.dumps(data, indent=2)


@tool("Save Daily Report")
def save_daily_report(report: str) -> str:
    """Save the daily marketing performance report."""
    os.makedirs("output/reports", exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"output/reports/daily-{date}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Daily Marketing Report - {date}\n\n")
        f.write(report)

    return f"Daily report saved to {filename}"
