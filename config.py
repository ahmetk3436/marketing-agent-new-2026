"""
Marketing Agent Pipeline - Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


# AI Models
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Search APIs
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Social Media
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")

# Email
MAILERLITE_API_KEY = os.getenv("MAILERLITE_API_KEY")

# Notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Server
PORT = int(os.getenv("PORT", 8080))

# Agent Settings
CONTENT_SCHEDULE = {
    "twitter": {"posts_per_day": 3, "best_hours": [9, 13, 18]},
    "instagram": {"posts_per_day": 1, "best_hours": [11, 19]},
    "linkedin": {"posts_per_day": 1, "best_hours": [8, 12]},
}

SEO_CONFIG = {
    "target_keywords_per_batch": 10,
    "min_word_count": 1500,
    "internal_links_per_page": 3,
}

EMAIL_CONFIG = {
    "welcome_delay_hours": 0,
    "nurture_interval_days": 2,
    "max_sequence_length": 7,
}
