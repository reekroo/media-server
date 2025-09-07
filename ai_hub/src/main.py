import asyncio
import argparse
import logging
from .app import App

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def _run(app: App, messages: list[str], job: str, **kwargs):
    res = await app.services.dispatcher.run(job, app=app, **kwargs)

    if not res:
        return
    
    if isinstance(res, list):
        for x in res:
            if isinstance(x, str) and x.strip():
                messages.append(x.strip())
    elif isinstance(res, str):
        if res.strip():
            messages.append(res.strip())

async def main():
    ap = argparse.ArgumentParser(description="AI Hub command-line runner.")
    ap.add_argument("cmd", choices=["brief", "media", "sys", "news", "news_tr", "entertainment", "dinner", "gaming", "weather", "logs"], help="The digest to run.")
    ap.add_argument("--to", choices=["console", "telegram"], default="console", help="Where to send the output.")
    ap.add_argument("--section", type=str, default=None, help="Specify a section for the news digest.")
    args = ap.parse_args()
    
    app = App()

    try:
        messages: list[str] = []

        if args.cmd == "brief": await _run(app, messages, "daily_brief")
        elif args.cmd == "weather": await _run(app, messages, "weather")
        elif args.cmd == "dinner": await _run(app, messages, "dinner")
        elif args.cmd == "media": await _run(app, messages, "media")
        elif args.cmd == "entertainment": await _run(app, messages, "entertainment")
        elif args.cmd == "news": await _run(app, messages, "news", section=args.section)
        elif args.cmd == "news_tr": await _run(app, messages, "news_tr")
        elif args.cmd == "gaming": await _run(app, messages, "gaming")
        elif args.cmd == "logs": await _run(app, messages, "logs")
        elif args.cmd == "sys": await _run(app, messages, "sys")

        if not messages:
            print("Job ran, but produced no output (empty or all feeds failed).")
            return

        for msg in messages:
            await app.send_notification(msg, send_to=args.to)
    finally:
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())