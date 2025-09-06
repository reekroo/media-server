import asyncio
import argparse
from .app import App

async def main():
    """CLI entry point to run digests on demand."""
    ap = argparse.ArgumentParser(description="AI Hub command-line runner.")
    ap.add_argument("cmd", choices=["brief", "media", "sys", "news", "gaming"], help="The digest to run.")
    ap.add_argument("--to", choices=["console", "telegram"], default="console", help="Where to send the output.")
    args = ap.parse_args()

    app = App()
    
    try:
        messages = []
        if args.cmd == "brief":
            messages.append(await app.run_daily_brief())
        elif args.cmd == "media":
            messages.append(await app.run_media_digest())
        elif args.cmd == "sys":
            messages.append(await app.run_sys_digest())
        elif args.cmd == "news":
            messages.extend(await app.run_news_digest())
        elif args.cmd == "gaming":
            messages.extend(await app.run_gaming_digest())

        if not messages or not any(messages):
            print("Job ran, but produced no output (e.g., disabled in config or no new items).")
            return

        for msg in messages:
            if msg:
                await app.send_notification(msg, send_to=args.to)

    finally:
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())