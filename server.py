"""
Marketing Agent Pipeline - MCP Server (SSE Transport)
=====================================================
Remote MCP server for marketing automation.
Exposes crew operations as tools.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

server = Server("marketing-agent")
BASE_DIR = Path(__file__).parent


# =============================================================================
# TOOL HANDLERS
# =============================================================================

async def run_crew_async(crew_func, **kwargs) -> str:
    """Run a crew function in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: crew_func(**kwargs))


async def handle_daily_content(arguments: Any) -> list[TextContent]:
    niche = arguments.get("niche", "AI and technology")
    try:
        from crews import run_daily_content_crew
        result = await run_crew_async(run_daily_content_crew, niche=niche)
        return [TextContent(type="text", text=f"# Daily Content Pipeline Complete\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def handle_seo_content(arguments: Any) -> list[TextContent]:
    topic = arguments.get("topic", "AI tools")
    num_articles = arguments.get("num_articles", 3)
    try:
        from crews import run_seo_crew
        result = await run_crew_async(run_seo_crew, topic=topic, num_articles=num_articles)
        return [TextContent(type="text", text=f"# SEO Content Pipeline Complete\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def handle_email_sequence(arguments: Any) -> list[TextContent]:
    product_name = arguments.get("product_name")
    value_prop = arguments.get("value_proposition", "")
    try:
        from crews import run_email_crew
        result = await run_crew_async(run_email_crew, product_name=product_name, value_prop=value_prop)
        return [TextContent(type="text", text=f"# Email Sequence Created\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def handle_analytics(arguments: Any) -> list[TextContent]:
    try:
        from crews import run_analytics_crew
        result = await run_crew_async(run_analytics_crew)
        return [TextContent(type="text", text=f"# Analytics Report\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def handle_full_pipeline(arguments: Any) -> list[TextContent]:
    niche = arguments.get("niche")
    product_name = arguments.get("product_name")
    value_prop = arguments.get("value_proposition", "")
    try:
        from crews import run_full_pipeline
        result = await run_crew_async(
            run_full_pipeline,
            niche=niche, product_name=product_name, value_prop=value_prop,
        )
        return [TextContent(type="text", text=f"# Full Marketing Pipeline Complete\n\n{result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="daily_content",
            description="Run daily content creation + social media scheduling pipeline. Researches trends, creates platform-specific posts, and schedules them.",
            inputSchema={
                "type": "object",
                "properties": {
                    "niche": {"type": "string", "description": "Target niche/industry (e.g., 'AI tools', 'fitness apps')"},
                },
                "required": ["niche"],
            },
        ),
        Tool(
            name="seo_content",
            description="Run SEO keyword research + article generation pipeline. Finds long-tail keywords and creates SEO-optimized articles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to create SEO content for"},
                    "num_articles": {"type": "number", "description": "Number of articles to generate (default: 3)", "default": 3},
                },
                "required": ["topic"],
            },
        ),
        Tool(
            name="email_sequence",
            description="Generate a 7-email nurture sequence for a product. Creates welcome, value, and conversion emails.",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Name of the product/service"},
                    "value_proposition": {"type": "string", "description": "What makes this product valuable"},
                },
                "required": ["product_name"],
            },
        ),
        Tool(
            name="analytics_report",
            description="Run daily analytics review. Analyzes all channels and sends summary via Telegram.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="full_pipeline",
            description="Run the FULL marketing pipeline - all 5 agents: content creation, social media scheduling, SEO, email sequences, and analytics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "niche": {"type": "string", "description": "Target niche"},
                    "product_name": {"type": "string", "description": "Product name"},
                    "value_proposition": {"type": "string", "description": "Value prop"},
                },
                "required": ["niche", "product_name"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    handlers = {
        "daily_content": handle_daily_content,
        "seo_content": handle_seo_content,
        "email_sequence": handle_email_sequence,
        "analytics_report": handle_analytics,
        "full_pipeline": handle_full_pipeline,
    }
    handler = handlers.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    return await handler(arguments)


# =============================================================================
# SSE TRANSPORT & HTTP APP
# =============================================================================

sse = SseServerTransport("/messages/")


async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def health(request):
    return JSONResponse({
        "status": "ok",
        "service": "marketing-agent",
        "tools": ["daily_content", "seo_content", "email_sequence", "analytics_report", "full_pipeline"],
    })


app = Starlette(
    routes=[
        Route("/health", endpoint=health),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    ],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Marketing Agent MCP Server (SSE) on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
