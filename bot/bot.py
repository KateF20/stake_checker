import asyncio
import logging
import telegram
import threading
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from settings.settings import BOT_TOKEN
from message import generate_stake_message
from database.database import remove_subscriber, add_subscriber, is_subscribed, get_all_subscribers
from events.stake_checker import start_history_fetcher, start_event_listener, set_new_stake_callback, new_stake_event


class Bot:
    def __init__(self):
        self.new_stake_event = new_stake_event
        self.application = ApplicationBuilder().token(BOT_TOKEN).build()
        self.add_handlers()
        self.start_stake_checker()

    def add_handlers(self):
        self.application.add_handler(CommandHandler('start', self.handle_start))
        self.application.add_handler(CommandHandler('get_chat_id', self.handle_get_chat_id))
        self.application.add_handler(CommandHandler('get_last_stake', self.handle_get_last_stake))
        self.application.add_handler(CommandHandler('subscribe', self.handle_subscribe))
        self.application.add_handler(CommandHandler('unsubscribe', self.handle_unsubscribe))

    def run(self):
        set_new_stake_callback(self.handle_new_stake)
        self.start_stake_checker()
        self.application.run_polling()

    def check_new_stakes(self):
        while True:
            self.new_stake_event.wait()
            asyncio.run(self.handle_new_stake())
            self.new_stake_event.clear()

    def start_stake_checker(self):
        self.history_thread = threading.Thread(target=start_history_fetcher)
        self.listener_thread = threading.Thread(target=start_event_listener)
        self.history_thread.start()
        self.listener_thread.start()
        threading.Thread(target=self.check_new_stakes).start()

    async def handle_new_stake(self):
        message = generate_stake_message()
        await self.broadcast_message(message)

    async def broadcast_message(self, message: str):
        subscriber_ids = get_all_subscribers()
        for chat_id in subscriber_ids:
            try:
                await self.application.bot.send_message(chat_id=chat_id, text=message)
            except Exception as e:
                logging.error(f"Error sending message to {chat_id}: {str(e)}")

    async def handle_start(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Huhu here")

    async def handle_get_chat_id(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(f"Your chat id is: {chat_id}")

    async def handle_get_last_stake(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        logging.info("there's a new stake")
        message = generate_stake_message()
        logging.info(f'new message is: {message}')
        await update.message.reply_text(message)

    async def handle_subscribe(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if not is_subscribed(chat_id):
            logging.info('checking subscribers')
            add_subscriber(chat_id)
            logging.info('successfully subscribed')
            await update.message.reply_text("You have subscribed to staking notifications.")
        else:
            await update.message.reply_text("You've already subscribed to staking notifications.")

    async def handle_unsubscribe(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if is_subscribed(chat_id):
            logging.info('checking unsubscribers')
            remove_subscriber(chat_id)
            logging.info('successfully unsubscribed')
            await update.message.reply_text("You have unsubscribed from staking notifications.")
        else:
            await update.message.reply_text("You are not subscribed to staking notifications.")


if __name__ == '__main__':
    bot = Bot()
    asyncio.run(bot.run())
