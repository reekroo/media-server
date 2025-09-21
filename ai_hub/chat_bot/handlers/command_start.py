from telegram import Update
from telegram.ext import ContextTypes

from core.logging import setup_logger, LOG_FILE_PATH
from core.settings import Settings

from ..messaging import reply_text_with_markdown
from ..state import get_available_digests

log = setup_logger(__name__, LOG_FILE_PATH)

def _fmt_cmds_block() -> str:
    return (
        "🔧 *Commands:*\n"
        "• `/help` — Show this help.\n"
        "• `/reset` — Reset chat history.\n"
        "• `/set_lang <lang>` — Set language (e.g., en, ru).\n"
        "• `/translate <to> <text>` — Translate text.\n"
        "• `/image <text>` — Generate an image from text.\n"
        "• `/digest <name> [count]` — Build a digest (e.g., `/digest news us 3`).\n"
        "• `/why <incident_id>` — Explain a system incident.\n"
    )

def _group_digests(names: list[str]) -> dict[str, list[str]]:
    groups = {
        "🗞️ *News digests:*": [],
        "🎮 *Entertainment:*": [],
        "🛠️ *System:*": [],
        "🍽️ *Daily:*": [],
        "📦 *Other:*": [],
    }

    for n in sorted(names):
        base = n.lower().strip()

        if base.startswith("news"):
            groups["🗞️ *News digests:*"].append(n)
        elif base in {"gaming", "entertainment", "media"}:
            groups["🎮 *Entertainment:*"].append(n)
        elif base in {"docker_status", "logs", "sys"}:
            groups["🛠️ *System:*"].append(n)
        elif base in {"daily", "dinner"}:
            groups["🍽️ *Daily:*"].append(n)
        else:
            groups["📦 *Other:*"].append(n)

    return {k: v for k, v in groups.items() if v}

def _fmt_digest_lines(digests: list[str]) -> str:
    return "\n".join(f"• `/digest {name}`" for name in digests)

def _fmt_digests_block(available: list[str]) -> str:
    if not available:
        return "_No digests configured yet._"

    grouped = _group_digests(available)
    parts = []
    for title, items in grouped.items():
        parts.append(f"{title}\n{_fmt_digest_lines(items)}")
    return "\n\n".join(parts)

def _build_help_message(available_digests: list[str]) -> str:
    header = (
        "✨ Welcome to *AI Hub Bot* ✨\n"
        "Your assistant for digests, translations, and system insights.\n\n"
    )

    cmds = _fmt_cmds_block()
    digests = _fmt_digests_block(available_digests)

    tip = (
        "\n\n💡 *Tip:* Type `/digest news` or simply say "
        "`Give me today’s news`."
    )

    return f"{header}{cmds}\n{digests}{tip}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        log.info(
            "🚨 Start command in chat_id=%s topic_id=%s text=%r",
            update.message.chat_id,
            update.message.message_thread_id,
            update.message.text,
        )

    settings: Settings = context.bot_data["settings"]
    available_digests = get_available_digests(settings)

    full_help_message = _build_help_message(available_digests)
    await reply_text_with_markdown(update, full_help_message)
