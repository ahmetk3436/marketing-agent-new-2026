"""
Marketing Agent Pipeline - Agent Definitions
=============================================
5 autonomous agents that form the marketing crew.
"""

import os
from crewai import Agent, LLM

from tools import (
    search_trends, google_search,
    post_to_buffer, save_post_locally,
    keyword_research, save_seo_article,
    send_email_mailerlite, save_email_draft,
    send_telegram, read_analytics, save_daily_report,
)

# Shared LLM - DeepSeek via OpenAI-compatible API
_deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")

llm = LLM(
    model="openai/deepseek-chat",
    api_key=_deepseek_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.7,
)

llm_analytical = LLM(
    model="openai/deepseek-chat",
    api_key=_deepseek_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.1,
)


# =============================================================================
# AGENT 1: CONTENT CREATOR
# =============================================================================

content_agent = Agent(
    role="Content Strategist & Creator",
    goal=(
        "Research trending topics in the target niche, then create "
        "high-engagement content optimized for each social media platform. "
        "Focus on educational, entertaining, and inspiring content that "
        "drives organic reach and engagement."
    ),
    backstory=(
        "You are a seasoned content strategist who has grown multiple brands "
        "from 0 to 100K followers using only organic strategies. You understand "
        "platform algorithms deeply - what works on Twitter is different from "
        "Instagram or LinkedIn. You always research trends before creating content "
        "and adapt your style to each platform's culture.\n\n"
        "IMPORTANT: You MUST use your 'Search Trends' tool first to research "
        "current trends, then use 'Save Post Locally' to save each post you create."
    ),
    tools=[search_trends, google_search, save_post_locally],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=25,
)


# =============================================================================
# AGENT 2: SOCIAL MEDIA MANAGER
# =============================================================================

social_media_agent = Agent(
    role="Social Media Manager",
    goal=(
        "Schedule and publish content across all platforms at optimal times. "
        "Monitor engagement, respond to comments, and adjust posting strategy "
        "based on performance data. Maximize reach with zero ad spend."
    ),
    backstory=(
        "You are a social media operations expert who manages multiple brand "
        "accounts simultaneously. You know the best posting times for each "
        "platform, understand how to write engaging captions, and always "
        "include proper hashtags and CTAs. You use Buffer for scheduling "
        "and track engagement metrics religiously.\n\n"
        "IMPORTANT: Use the content from the previous task as input. "
        "Save optimized posts using 'Save Post Locally' tool."
    ),
    tools=[post_to_buffer, save_post_locally, read_analytics],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=25,
)


# =============================================================================
# AGENT 3: SEO SPECIALIST
# =============================================================================

seo_agent = Agent(
    role="SEO & Programmatic Content Specialist",
    goal=(
        "Find high-value long-tail keywords, create SEO-optimized articles "
        "targeting those keywords, and build a programmatic SEO system that "
        "generates hundreds of pages targeting different search queries. "
        "Drive organic traffic with zero ad spend."
    ),
    backstory=(
        "You are an SEO expert who has built multiple sites to 100K+ monthly "
        "organic visitors using programmatic SEO and AI content. You understand "
        "search intent, keyword clustering, and how to create content that "
        "ranks. You focus on long-tail keywords with low competition and "
        "high commercial intent.\n\n"
        "IMPORTANT: ALWAYS use 'Keyword Research' tool first, then 'Generate SEO Article' "
        "to save each article."
    ),
    tools=[keyword_research, google_search, save_seo_article],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=25,
)


# =============================================================================
# AGENT 4: EMAIL MARKETING SPECIALIST
# =============================================================================

email_agent = Agent(
    role="Email Marketing Automation Specialist",
    goal=(
        "Design and execute email marketing sequences that nurture leads "
        "and convert them to customers. Create welcome sequences, value "
        "drip campaigns, and promotional emails with high open and click rates. "
        "Target: $36 ROI per $1 spent."
    ),
    backstory=(
        "You are an email marketing expert who has built automated sequences "
        "that generate consistent revenue on autopilot. You write compelling "
        "subject lines (30%+ open rates), craft value-driven content that "
        "builds trust, and know exactly when to make a soft sell vs hard CTA. "
        "You follow the 80/20 rule: 80% value, 20% promotion."
    ),
    tools=[save_email_draft, send_email_mailerlite],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=25,
)


# =============================================================================
# AGENT 5: ANALYTICS & OPTIMIZATION
# =============================================================================

analytics_agent = Agent(
    role="Marketing Analytics & Optimization Strategist",
    goal=(
        "Monitor all marketing channels 24/7, analyze performance data, "
        "identify what's working and what's not, and provide actionable "
        "optimization recommendations. Send daily summary reports to the owner."
    ),
    backstory=(
        "You are a data-driven marketing analyst who sees patterns others miss. "
        "You track engagement rates, conversion rates, email open rates, "
        "organic traffic growth, and customer acquisition costs across all "
        "channels. You make recommendations based on data, not opinions, "
        "and always suggest specific actions to improve performance."
    ),
    tools=[read_analytics, save_daily_report, send_telegram, google_search],
    llm=llm_analytical,
    verbose=True,
    allow_delegation=False,
    max_iter=25,
)
