"""
Marketing Agent Pipeline - Crew Definitions
=============================================
Different crews for different marketing workflows.
"""

from crewai import Crew, Task

from agents import (
    content_agent, social_media_agent,
    seo_agent, email_agent, analytics_agent,
)


# =============================================================================
# TASKS
# =============================================================================

def create_content_task(niche: str, platforms: list[str] = None) -> Task:
    """Create a content generation task."""
    platforms = platforms or ["twitter", "instagram", "linkedin"]
    return Task(
        description=(
            f"Research the latest trends in '{niche}' and create engaging content "
            f"for these platforms: {', '.join(platforms)}.\n\n"
            f"For each platform, create:\n"
            f"- Twitter: 3 tweets (max 280 chars each, include hashtags)\n"
            f"- Instagram: 1 caption (with emojis, hashtags, CTA)\n"
            f"- LinkedIn: 1 professional post (thought leadership style)\n\n"
            f"Research trending topics first, then create platform-optimized content. "
            f"Save each post using the save tool."
        ),
        expected_output=(
            "A set of platform-specific posts saved to files, with a summary "
            "of what was created and why these topics were chosen."
        ),
        agent=content_agent,
    )


def create_social_task(posts_summary: str = "") -> Task:
    """Create a social media scheduling task."""
    return Task(
        description=(
            f"Review the generated content and schedule it for posting.\n\n"
            f"Context from content team: {posts_summary}\n\n"
            f"For each post:\n"
            f"1. Review and optimize the copy if needed\n"
            f"2. Add appropriate hashtags if missing\n"
            f"3. Schedule via Buffer at optimal times\n"
            f"4. If Buffer is not configured, save posts locally with scheduling notes\n\n"
            f"Optimal posting times:\n"
            f"- Twitter: 9 AM, 1 PM, 6 PM\n"
            f"- Instagram: 11 AM, 7 PM\n"
            f"- LinkedIn: 8 AM, 12 PM"
        ),
        expected_output=(
            "Confirmation of posts scheduled or saved, with platform, "
            "time, and content summary for each."
        ),
        agent=social_media_agent,
    )


def create_seo_task(topic: str, num_articles: int = 3) -> Task:
    """Create an SEO content generation task."""
    return Task(
        description=(
            f"Create {num_articles} SEO-optimized articles about '{topic}'.\n\n"
            f"Steps:\n"
            f"1. Research keywords using the keyword tool\n"
            f"2. Find long-tail keywords with high intent\n"
            f"3. For each article:\n"
            f"   - Write 1500+ word comprehensive article\n"
            f"   - Include target keyword in title, H2s, and naturally in body\n"
            f"   - Add internal linking suggestions\n"
            f"   - Include FAQ section targeting 'People Also Ask' queries\n"
            f"   - Save using the article save tool\n"
        ),
        expected_output=(
            "Articles saved with target keywords, word count, "
            "and SEO optimization notes for each."
        ),
        agent=seo_agent,
    )


def create_email_task(product_name: str, value_proposition: str) -> Task:
    """Create an email sequence generation task."""
    return Task(
        description=(
            f"Create a 7-email nurture sequence for '{product_name}'.\n\n"
            f"Value proposition: {value_proposition}\n\n"
            f"Email sequence:\n"
            f"1. Welcome email (immediate) - introduce brand, set expectations\n"
            f"2. Value email #1 (day 2) - educational content, no selling\n"
            f"3. Case study (day 4) - social proof, results\n"
            f"4. Value email #2 (day 6) - more education, tips\n"
            f"5. Soft CTA (day 8) - introduce product naturally\n"
            f"6. Promotion (day 10) - clear offer, urgency\n"
            f"7. Feedback (day 14) - ask for input, re-engage\n\n"
            f"For each email, write compelling subject line and full body. "
            f"Save each as a draft."
        ),
        expected_output=(
            "7 email drafts saved with subject lines, send timing, "
            "and expected open/click rates."
        ),
        agent=email_agent,
    )


def create_analytics_task() -> Task:
    """Create a daily analytics review task."""
    return Task(
        description=(
            "Review all marketing performance data and create a daily report.\n\n"
            "Analyze:\n"
            "1. Social media: engagement rates, follower growth, top posts\n"
            "2. Email: open rates, click rates, unsubscribes\n"
            "3. SEO: organic traffic, keyword rankings, new pages indexed\n"
            "4. Overall: conversion rates, lead count, revenue if available\n\n"
            "Then:\n"
            "- Identify top 3 wins\n"
            "- Identify top 3 areas for improvement\n"
            "- Provide specific action items for tomorrow\n"
            "- Save the report and send a Telegram summary to the owner"
        ),
        expected_output=(
            "Daily report saved and Telegram notification sent with "
            "key metrics and action items."
        ),
        agent=analytics_agent,
    )


# =============================================================================
# CREWS
# =============================================================================

def run_daily_content_crew(niche: str) -> str:
    """Run the daily content creation + scheduling pipeline."""
    content_task = create_content_task(niche)
    social_task = create_social_task()

    crew = Crew(
        agents=[content_agent, social_media_agent],
        tasks=[content_task, social_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def run_seo_crew(topic: str, num_articles: int = 3) -> str:
    """Run SEO keyword research + article generation pipeline."""
    seo_task = create_seo_task(topic, num_articles)

    crew = Crew(
        agents=[seo_agent],
        tasks=[seo_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def run_email_crew(product_name: str, value_prop: str) -> str:
    """Run email sequence generation pipeline."""
    email_task = create_email_task(product_name, value_prop)

    crew = Crew(
        agents=[email_agent],
        tasks=[email_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def run_analytics_crew() -> str:
    """Run daily analytics review pipeline."""
    analytics_task = create_analytics_task()

    crew = Crew(
        agents=[analytics_agent],
        tasks=[analytics_task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def run_full_pipeline(niche: str, product_name: str, value_prop: str) -> str:
    """Run the complete marketing pipeline - all 5 agents."""
    crew = Crew(
        agents=[
            content_agent, social_media_agent,
            seo_agent, email_agent, analytics_agent,
        ],
        tasks=[
            create_content_task(niche),
            create_social_task(),
            create_seo_task(niche),
            create_email_task(product_name, value_prop),
            create_analytics_task(),
        ],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
