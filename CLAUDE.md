# Marketing Agent Pipeline

AI-powered autonomous marketing system with 5 specialized agents.

## Architecture
- **Framework**: CrewAI (multi-agent orchestration)
- **LLM**: DeepSeek (cheap, good quality)
- **Tools**: Tavily, Serper (search), Buffer (social), MailerLite (email)

## Agents
1. **Content Agent** - Trend research + content creation
2. **Social Media Agent** - Post scheduling + engagement
3. **SEO Agent** - Keyword research + article generation
4. **Email Agent** - Nurture sequence creation
5. **Analytics Agent** - Performance monitoring + reporting

## Key Files
- `agents.py` - Agent definitions with roles, goals, tools
- `crews.py` - Crew compositions and task definitions
- `tools.py` - Custom tools (search, Buffer, MailerLite, Telegram)
- `server.py` - SSE MCP server for remote access
- `main.py` - CLI entry point
- `config.py` - Configuration and settings

## MCP Tools
- `daily_content(niche)` - Content + social media pipeline
- `seo_content(topic, num_articles)` - SEO article pipeline
- `email_sequence(product_name, value_proposition)` - Email nurture
- `analytics_report()` - Daily performance review
- `full_pipeline(niche, product_name, value_proposition)` - All 5 agents

## Deploy
```bash
git push origin main
curl -X POST "http://89.47.113.196:8000/api/v1/deploy" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -d '{"uuid":"MARKETING_APP_UUID","force":true}'
```
