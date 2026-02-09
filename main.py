"""
Marketing Agent Pipeline - CLI Entry Point
===========================================
Run marketing crews from the command line.
"""

import argparse
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Marketing Agent Pipeline - AI-Powered Marketing Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Daily content creation
  python main.py content --niche "AI tools for developers"

  # SEO article generation
  python main.py seo --topic "best AI marketing tools 2026" --articles 5

  # Email nurture sequence
  python main.py email --product "MarketBot" --value "AI marketing on autopilot"

  # Analytics report
  python main.py analytics

  # Full pipeline
  python main.py full --niche "AI tools" --product "MarketBot" --value "AI marketing"
        """,
    )

    sub = parser.add_subparsers(dest="command", help="Pipeline to run")

    # Content
    p_content = sub.add_parser("content", help="Daily content creation + scheduling")
    p_content.add_argument("--niche", required=True, help="Target niche")

    # SEO
    p_seo = sub.add_parser("seo", help="SEO keyword research + article generation")
    p_seo.add_argument("--topic", required=True, help="Topic for articles")
    p_seo.add_argument("--articles", type=int, default=3, help="Number of articles")

    # Email
    p_email = sub.add_parser("email", help="Email nurture sequence generation")
    p_email.add_argument("--product", required=True, help="Product name")
    p_email.add_argument("--value", default="", help="Value proposition")

    # Analytics
    sub.add_parser("analytics", help="Daily analytics review")

    # Full
    p_full = sub.add_parser("full", help="Run full marketing pipeline")
    p_full.add_argument("--niche", required=True)
    p_full.add_argument("--product", required=True)
    p_full.add_argument("--value", default="")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    console.print(Panel("MARKETING AGENT PIPELINE", style="bold green"))

    from crews import (
        run_daily_content_crew, run_seo_crew,
        run_email_crew, run_analytics_crew, run_full_pipeline,
    )

    if args.command == "content":
        console.print(f"[bold]Running content pipeline for:[/bold] {args.niche}")
        result = run_daily_content_crew(args.niche)

    elif args.command == "seo":
        console.print(f"[bold]Running SEO pipeline for:[/bold] {args.topic}")
        result = run_seo_crew(args.topic, args.articles)

    elif args.command == "email":
        console.print(f"[bold]Creating email sequence for:[/bold] {args.product}")
        result = run_email_crew(args.product, args.value)

    elif args.command == "analytics":
        console.print("[bold]Running analytics review...[/bold]")
        result = run_analytics_crew()

    elif args.command == "full":
        console.print(f"[bold]Running FULL pipeline for:[/bold] {args.niche}")
        result = run_full_pipeline(args.niche, args.product, args.value)

    console.print(Panel(str(result)[:2000], title="Result", style="green"))


if __name__ == "__main__":
    main()
