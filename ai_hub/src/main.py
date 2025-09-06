import asyncio
import argparse
import logging
from .app import App

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    ap = argparse.ArgumentParser(description="AI Hub command-line runner.")
    ap.add_argument("cmd", choices=["brief", "media", "sys", "news", "news_tr", "entertainment", "dinner", "gaming", "weather", "logs"], help="The digest to run.")
    ap.add_argument("--to", choices=["console", "telegram"], default="console", help="Where to send the output.")
    ap.add_argument("--section", type=str, default=None, help="Specify a section for the news digest.")
    args = ap.parse_args()
    
    app = App()

    try:
        messages = []
        if args.cmd == "brief": messages.append(await app.run_daily_brief())
        elif args.cmd == "media": messages.append(await app.run_media_digest())
        elif args.cmd == "sys": messages.append(await app.run_sys_digest())
        elif args.cmd == "news": messages.extend(await app.run_news_digest(section=args.section))
        elif args.cmd == "gaming": messages.extend(await app.run_gaming_digest())
        elif args.cmd == "weather": messages.append(await app.run_weather_summary())
        elif args.cmd == "logs": messages.append(await app.run_log_digest())
        elif args.cmd == "news_tr": messages.extend(await app.run_turkish_news_digest())
        elif args.cmd == "entertainment": messages.append(await app.run_entertainment_digest())
        elif args.cmd == "dinner": messages.append(await app.run_dinner_digest())

        final_messages = [msg for msg in messages if msg and msg.strip()]
        
        if not final_messages:
            print("Job ran, but produced no output (e.g., network error, disabled in config or no new items).")
            return
        
        for msg in final_messages:
            await app.send_notification(msg, send_to=args.to)
    finally:
        await app.close_resources()

if __name__ == "__main__":
    asyncio.run(main())