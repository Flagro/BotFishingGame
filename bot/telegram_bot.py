import random
from datetime import datetime
import pymongo
import motor.motor_asyncio

from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application


class TelegramEpicFishingBot:
    def __init__(self, telegram_token, mongodb_url):
        self.telegram_token = telegram_token
        # Initialize MongoDB client and select the database and collection
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        db = client.get_database('async_fishing_game_db')
        self.inventory_collection = db.get_collection('inventory')

        self.commands = [
            BotCommand(command="start", description="Start the fishing adventure and get instructions."),
            BotCommand(command="fish", description="Try your luck and fish something from the sea."),
            BotCommand(command="inventory", description="Check your current inventory of catches."),
        ]

        self.handlers = [
            CommandHandler("start", self.start),
            CommandHandler("fish", self.fish),
            CommandHandler("inventory", self.inventory)
        ]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_name = update.effective_user.first_name
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {user_name}!")

    async def fish(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        fish_types = [
            'Salmon', 'Trout', 'Bass', 'Catfish', 'Seahorse', 'Clownfish',
            'Cod', 'Eel', 'Flounder', 'Mackerel', 'Marlin', 'Swordfish', 
            'Octopus', 'Jellyfish', 'Starfish', 'Squid', 'Shark', 'Dolphin',
            'Whale', 'Tuna', 'Crab', 'Lobster', 'Shrimp', 'Oyster', 'Clam',
            'Snapper', 'Grouper', 'Barracuda', 'Sardine', 'Herring', 'Anchovy',
            'Pufferfish', 'Stingray', 'Boot', 'Empty Bottle', 'Tree Branch',
            'Seaweed', 'Coral', 'Pearl', 'Old Can', 'Plastic Bag', 'Tire',
            'Message in a Bottle', 'Sunken Treasure Chest', 'Anchor',
            'Shipwreck Remains', 'Pirate Hat', 'Fishbone', 'Fishing Net',
            'Submarine Toy', 'Golden Coin'
        ]

        caught_fish = random.choice(fish_types)
        weight = round(random.uniform(1, 5), 2)  # weight in kg
        caught_at = datetime.utcnow()
        
        # Insert the caught fish into the inventory collection
        self.inventory_collection.insert_one({
            'user_id': user_id,
            'fish_type': caught_fish,
            'weight': weight,
            'caught_at': caught_at
        })

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You caught a {caught_fish}!\nWeight: {weight} kg')

    async def inventory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        try:
            user_inventory_cursor = self.inventory_collection.find({'user_id': user_id})
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
                f"Caught At: {caught_at}\n"
            )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=inventory_message)

    async def post_init(self, application: Application):
        """
        Post initialization hook for the bot.
        """
        await application.bot.set_my_commands(self.commands)

    def run(self):
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """
        application = ApplicationBuilder() \
            .token(self.telegram_token) \
            .post_init(self.post_init) \
            .build()
    
        for handler in self.handlers:
            application.add_handler(handler)
        
        application.run_polling()
