#!/usr/bin/env python3
"""
AI Customer Support Agent — Demo CLI
Run: python main.py
"""

import os
import sys
from agent import CustomerSupportAgent

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False


def print_response(result: dict):
    """Pretty-print the agent's response."""
    cls = result["classification"]
    header = (
        f"[{cls['urgency'].upper()}] "
        f"Topic: {cls['topic']} | "
        f"Sources: {', '.join(result['sources']) if result['sources'] else 'KB'}"
    )

    if HAS_RICH:
        console.print(Panel(
            Markdown(result["reply"]),
            title=header,
            border_style="cyan",
        ))
        console.print(f"Session: [dim]{result['session_id']}[/dim]")
    else:
        print("─" * 50)
        print(header)
        print("─" * 50)
        print(result["reply"])
        print(f"\nSession: {result['session_id']}")


def show_help():
    print("""
Commands:
  <your message>    — Ask the support agent
  /stats            — Show session statistics
  /help             — Show this help
  /quit             — Exit

Examples:
  > Where is my order?
  > Şifremi unuttum, yardım eder misiniz?
  > My payment is not going through!
""")


def main():
    agent = CustomerSupportAgent()
    session_id = None

    if HAS_RICH:
        console.print(Panel(
            "[bold cyan]AI Customer Support Agent[/bold cyan]\n"
            "Type your question or type [yellow]/help[/yellow]",
            border_style="cyan",
        ))
    else:
        print("AI Customer Support Agent — type /help for commands")

    while True:
        try:
            user_input = input("\n> " if HAS_RICH else "\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue

        if user_input == "/quit":
            print("Goodbye!")
            break
        elif user_input == "/help":
            show_help()
            continue
        elif user_input == "/stats":
            stats = agent.storage.get_stats()
            if HAS_RICH:
                console.print(f"[green]📊 Messages: {stats['total_messages']}, Sessions: {stats['total_sessions']}[/green]")
            else:
                print(f"📊 Messages: {stats['total_messages']}, Sessions: {stats['total_sessions']}")
            continue

        # Process
        result = agent.handle(user_input, session_id)
        if session_id is None:
            session_id = result["session_id"]

        print_response(result)


if __name__ == "__main__":
    main()
