import os
import random
from datetime import datetime
from dotenv import load_dotenv
import logging
import pymongo
from pymongo import MongoClient

from telegram import Update, ForceReply
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Updater, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

# Load environment variables from .env file
load_dotenv()

# Read environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MONGODB_URI = os.getenv('MONGODB_URI')

# Initialize MongoDB client and select the database and collection
client = MongoClient(MONGODB_URI)
db = client.get_database('fishing_game_db')
inventory_collection = db.get_collection('inventory')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {user_name}!")


async def fish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    fish_types = ['Salmon', 'Trout', 'Bass', 'Catfish']
    caught_fish = random.choice(fish_types)
    weight = round(random.uniform(1, 5), 2)  # weight in kg
    length = round(random.uniform(20, 100), 2)  # length in cm
    caught_at = datetime.utcnow()
    
    # Insert the caught fish into the inventory collection
    inventory_collection.insert_one({
        'user_id': user_id,
        'fish_type': caught_fish,
        'weight': weight,
        'length': length,
        'caught_at': caught_at
    })

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You caught a {caught_fish}!\nWeight: {weight} kg\nLength: {length} cm')


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        user_inventory_cursor = inventory_collection.find({'user_id': user_id})
        user_inventory = await user_inventory_cursor.to_list(length=100)  # Adjust length as needed
    except pymongo.errors.PyMongoError as e:
        print(f"MongoDB Error: {e}")
        await update.message.reply_text('An error occurred while fetching your inventory!')
        return

    if not user_inventory:
        await update.message.reply_text('Your inventory is empty!')
        return
    
    inventory_message = 'Your Inventory:\n'
    for item in user_inventory:
        caught_at = item['caught_at'].strftime('%Y-%m-%d %H:%M:%S')
        inventory_message += (
            f"Fish Type: {item['fish_type']}, "
            f"Weight: {item['weight']} kg, "
            f"Length: {item['length']} cm, "
            f"Caught At: {caught_at}\n"
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=inventory_message)



def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    handlers = [
        CommandHandler("start", start),
        CommandHandler("fish", fish),
        CommandHandler("inventory", inventory)
    ]

    for handler in handlers:
        application.add_handler(handler)
    
    application.run_polling()


if __name__ == '__main__':
    main()
