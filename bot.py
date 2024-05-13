import logging
import asyncio
from telegram import Update,ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
import google.generativeai as genai


BOT_TOKEN = "BOT TOKEN HERE" #please note, this is the main bot token that is intended for AI request and response 
genai.configure(api_key='YOUR API KEY')

support='' #your or someone's telegram username to contact in case of any issue.
waiting_messages = {}


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Please send me a message, I will respond back!",
        reply_markup=ForceReply(selective=True),
    )
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hi!, We are really sorry if you are facing any issue. Please contact our support team {support}")


async def echo(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    waiting_message=await update.message.reply_text("Please wait a moment...")
    waiting_messages[update.effective_chat.id]=waiting_message.message_id

    try:
        response = await asyncio.to_thread(send_genai_message, user_message)
        ai_response = response.text
        chat_id = update.effective_chat.id
        wait_message_id = waiting_messages.get(chat_id)
        
        if wait_message_id:
            await context.bot.delete_message(chat_id=chat_id, message_id=wait_message_id)
        await update.message.reply_text(ai_response)
        
        
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        await update.message.reply_text("Sorry, I encountered an issue. Please try again later.")


def send_genai_message(user_message: str):
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat()
    return chat.send_message(user_message)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()