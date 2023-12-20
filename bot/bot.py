import asyncio
import telegram
from telegram.ext import ApplicationBuilder, Application, ContextTypes, CommandHandler

from settings.settings import BOT_TOKEN
from database.database import get_last_stake


class Bot:
    def __init__(self):
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()
        self.application.add_handler(CommandHandler('start', self.handle_start))
        self.application.add_handler(CommandHandler("get_chat_id", self.handle_get_chat_id))
        self.application.add_handler(CommandHandler("get_last_stake", self.handle_last_stake))
        # self.application.add_handler(CommandHandler('subscribe', self.handleNotify))
        # self.application.add_handler(CommandHandler('unsubscribe', self.handleNoNotify))

    def run(self):
        self.application.run_polling()
        self.setup_command()

    async def setup_command(self):
        await self.application.bot.set_my_commands([
            telegram.BotCommand("get_chat_id", "Get the current chat id"),
            telegram.BotCommand("get_last_stake", "Get the last stake on the contract"),
            telegram.BotCommand("subscribe", "Enable subscription in the current chat"),
            telegram.BotCommand("unsubscribe", "Disable subscription in the current chat"),
        ])

    async def handle_start(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        message = """
                Huhu here
                """
        await update.message.reply_text(message)

    async def handle_get_chat_id(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        message = """
        Your chat id is: {0}
        """.format(update.effective_chat.id)
        await update.message.reply_text(message)

    async def handle_last_stake(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        last_stake = get_last_stake()
        if last_stake is not None:
            duration_seconds = last_stake.unstake_timestamp - int(last_stake.timestamp.timestamp())
            duration_days = duration_seconds // (24 * 3600)

            amount_staked_eth = last_stake.amount_staked / 10 ** 18

            message = (
                f"NEW $PAAL STAKE!\n\n"
                f"🤖 Amount Staked\n"
                f"{amount_staked_eth:.2e} ETH| ${last_stake.usd_value:.2e}\n\n"
                f"⏰ Duration {duration_days} days\n\n"
                f"🔒 Total Staked...% | $...")

        else:
            message = "No stakes found."

        await update.message.reply_text(message)


if __name__ == '__main__':
    bot = Bot()
    asyncio.run(bot.run())
