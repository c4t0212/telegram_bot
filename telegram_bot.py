import os
import database
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class TelegramBot:
    def __init__(self) -> None:
        token = os.getenv('TELEGRAM_TOKEN') 
        self.app = ApplicationBuilder().token(token).build()
        state_name = ['TYPING_STATE', 'CHOOSING_STATE']
        [setattr(self, state_name[i], i) for i in range(len(state_name))]
        self.db = database.db
    

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = \
        """
        /subscribe - 訂閱消息
        """
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    async def subscribeMessage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='輸入要訂閱的訊息')
        return self.TYPING_STATE
    
    async def typing_state_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = update.message.text
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        context.user_data['subscribe_message'] = response
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= f'是否訂閱訊息: {response}',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('確定', callback_data='確定'), InlineKeyboardButton('取消', callback_data='取消')],
            ])
        )
        return self.CHOOSING_STATE

    async def confrim_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query.data == '確定':
            subscribers_message = context.user_data['subscribe_message']
            # subscribers_chat_id = self.db.get(subscribers_message, None)
            # print(subscribers_message)
            notify_db = self.db['notify']
            mango_query = {
                "selector": {
                    "message": subscribers_message
                },
                "fields": [
                    "_id",
                    "_rev",
                    "message",
                    "chat_id"
                ]
            }
            result = list(notify_db.find(mango_query))
            if len(result) == 0:
                result = {
                    'message': subscribers_message,
                    'chat_id': []
                }
            else:
                result = result[0]
            subscribers_chat_id = result['chat_id']
            if update.effective_chat.id not in subscribers_chat_id:
                subscribers_chat_id.append(update.effective_chat.id)
                await update.effective_message.edit_text(f'訂閱成功消息: "{subscribers_message}"')
            else:
                await update.effective_message.edit_text(f'已訂閱過消息: "{subscribers_message}"')
            result['chat_id'] = subscribers_chat_id
            notify_db.save(result)


        else:
            await update.effective_message.edit_text('已取消')
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='取消')
        return ConversationHandler.END

    def run(self) -> None:
        logging.info("Telegram bot running")
        start_handler = [
            CommandHandler('start', self.start),
            CommandHandler('help', self.help),
            ConversationHandler(
                entry_points=[CommandHandler('subscribe', self.subscribeMessage)],
                states={
                    self.TYPING_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.typing_state_response)],
                    self.CHOOSING_STATE: [CallbackQueryHandler(self.confrim_subscribe)]
                },
                fallbacks=[CommandHandler('cancel', self.cancel)]
            ),
        ]
        [self.app.add_handler(handler) for handler in start_handler]
        self.app.run_polling()

bot = TelegramBot()