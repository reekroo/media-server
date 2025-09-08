# src/main.py
from __future__ import annotations

import asyncio
import argparse
import logging
from typing import List

from .app import App

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def _run(app: App, messages: List[str], job: str, **kwargs) -> None:
    chunks = await app.services.dispatcher.run(job, app=app, **kwargs)
    if not chunks:
        logger.info("Job '%s' produced no textual output.", job)
    messages.extend(chunks)

async def main() -> None:
    parser = argparse.ArgumentParser(prog="ai_hub")
    parser.add_argument(
        "cmd",
        choices=[
            "brief",
            "dinner",
            "weather",
            "quakes",
            "media",
            "entertainment",
            "news",
            "news_tr",
            "gaming",
            "logs",
            "sys",
        ],
        help="Which job to run",
    )
    parser.add_argument("--to", choices=["console", "telegram"], default="console",
                        help="Where to send output (telegram/console)")
    parser.add_argument("--section", default=None,
                        help="Optional section filter for news/news_tr")

    args = parser.parse_args()

    app = App()
    messages: List[str] = []

    try:
        if args.cmd == "brief": await _run(app, messages, "daily_brief")
        elif args.cmd == "dinner": await _run(app, messages, "dinner")
        elif args.cmd == "weather": await _run(app, messages, "weather")
        elif args.cmd == "quakes": await _run(app, messages, "quakes")
        elif args.cmd == "media": await _run(app, messages, "media")
        elif args.cmd == "entertainment": await _run(app, messages, "entertainment")
        elif args.cmd == "news": await _run(app, messages, "news", section=args.section)
        elif args.cmd == "news_tr": await _run(app, messages, "news_tr")
        elif args.cmd == "gaming": await _run(app, messages, "gaming")
        elif args.cmd == "logs": await _run(app, messages, "logs")
        elif args.cmd == "sys": await _run(app, messages, "sys")
        else:
            logger.error("Unknown command: %s", args.cmd)
            return

        if not messages:
            print("Job ran, but produced no output (empty or all feeds failed).")
            return

        logger.info("Collected %d message chunk(s) to deliver via %s.", len(messages), args.to)
        for msg in messages:
            await app.send_notification(msg, send_to=args.to)

    finally:
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())
