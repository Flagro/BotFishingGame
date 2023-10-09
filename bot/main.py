import os
import logging
from dotenv import load_dotenv
from telegram_bot import TelegramEpicFishingBot


def main():
    # Load environment variables from .env file
    load_dotenv()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    bot = TelegramEpicFishingBot(telegram_token=os.getenv('TELEGRAM_TOKEN'),
                                 mongodb_url="mongodb://{}:{}".format(os.getenv("MONGODB_HOST"), os.getenv("MONGODB_PORT")),
                                 items_file_path="./data/sea_items.json")
    
    bot.run()


if __name__ == '__main__':
    main()
