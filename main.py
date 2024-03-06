import logging
from decouple import config
from bot.telegram_bot import TelegramEpicFishingBot


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    bot = TelegramEpicFishingBot(
        telegram_token=config("TELEGRAM_TOKEN"),
        mongodb_url="mongodb://{}:{}".format(
            config("MONGODB_HOST"), config("MONGODB_PORT")
        ),
        items_file_path="./data/sea_items.json",
    )

    bot.run()


if __name__ == "__main__":
    main()
