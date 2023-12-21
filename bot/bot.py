import asyncio
import threading
import telegram
from decimal import Decimal
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from settings.settings import BOT_TOKEN, EXCHANGE_RATE
from database.database import get_last_stake, get_total_staked
from events.stake_checker import start_history_fetcher, start_event_listener


class Bot:
    def __init__(self):
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()
        self.add_handlers()
        self.start_stake_checker()

    def add_handlers(self):
        self.application.add_handler(CommandHandler('start', self.handle_start))
        self.application.add_handler(CommandHandler('get_chat_id', self.handle_get_chat_id))
        self.application.add_handler(CommandHandler('get_last_stake', self.handle_get_last_stake))

    def start_stake_checker(self):
        self.history_thread = threading.Thread(target=start_history_fetcher)
        self.listener_thread = threading.Thread(target=start_event_listener)
        self.history_thread.start()
        self.listener_thread.start()

    async def handle_start(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Huhu here")

    async def handle_get_chat_id(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"Your chat id is: {chat_id}")

    async def handle_get_last_stake(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        last_stake = get_last_stake()
        total_staked = get_total_staked()

        if last_stake is not None:
            duration_seconds = last_stake.unstake_timestamp - int(last_stake.timestamp.timestamp())
            duration_days = duration_seconds // (24 * 3600)

            amount_staked_eth = last_stake.amount_staked / 10 ** 18
            total_staked_eth = total_staked / 10 ** 18
            total_staked_usd = total_staked_eth * Decimal(EXCHANGE_RATE)

            message = (
                f"NEW $PAAL STAKE!\n\n"
                f"🤖 Amount Staked\n"
                f"{amount_staked_eth:.2e} ETH| ${last_stake.usd_value:.2e}\n\n"
                f"⏰ Duration {duration_days} days\n\n"
                f"🔒 Total Staked {total_staked_eth:.2f} ETH| ${total_staked_usd:.2f}")

        else:
            message = "No stakes found."

        await update.message.reply_text(message)

    def run(self):
        self.application.run_polling()


if __name__ == '__main__':
    bot = Bot()
    asyncio.run(bot.run())
