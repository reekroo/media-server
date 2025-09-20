from telegram import Update
from telegram.ext import ContextTypes

from core.settings import Settings
from functions.local_data.reader import read_json_async
from chat_bot.rpc_client import ChatRpcClient, ui_error_message
from chat_bot.messaging import reply_text_with_markdown

MSG_USAGE =              "🟦 Usage: /why <incident_id>"
MSG_INCIDENT_NOT_FOUND = "🟨 Incident '{inc_id}' not found."
MSG_ANALYZING =          "🧠 Analyzing incident, please wait..."

async def why_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not context.args:
        await update.message.reply_text(MSG_USAGE)
        return

    inc_id = context.args[0]

    settings: Settings = context.bot_data["settings"]
    rpc_client: ChatRpcClient = context.bot_data["rpc_client"]
    
    inc_path = settings.STATE_DIR / "incidents" / f"{inc_id}.json"

    incident_data = await read_json_async(inc_path)
    if not incident_data:
        await update.message.reply_text(MSG_INCIDENT_NOT_FOUND.format(inc_id=inc_id))
        return

    await update.message.reply_text(MSG_ANALYZING)

    response = await rpc_client.call(
        "assist.digest",
        kind="clarify",
        params={"incident": incident_data},
    )

    if not response.get("ok"):
        await reply_text_with_markdown(update, ui_error_message(response.get("error", {})))
        return

    explanation = response.get("result", "An unexpected error occurred: empty result from AI.")
    await reply_text_with_markdown(update, str(explanation))