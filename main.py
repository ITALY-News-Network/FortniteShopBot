import telebot
import os
import configparser
import fortnite_api

MAIN_SECTION_NAME = 'GENERAL'
BOT_TOKEN_CONFIGURATION_KEY = 'bot_token'
CHANNEL_ID_CONFIGURATION_KEY = 'channel_id'
CONFIGURATION_NAME = 'config.ini'
bot_token = ''
channel_id = 0
config = None
api = None
shop = None
SHOP_LANGUAGE_DICTIONARY = fortnite_api.GameLanguage.ITALIAN


def save_config():
    with open(CONFIGURATION_NAME, 'w') as configfile:
        config.write(configfile)


def setup_config():
    if not os.path.exists(CONFIGURATION_NAME):
        save_config()

    if not config.has_section(MAIN_SECTION_NAME):
        config.add_section(MAIN_SECTION_NAME)

    if not config.has_option(MAIN_SECTION_NAME, BOT_TOKEN_CONFIGURATION_KEY):
        config.set(MAIN_SECTION_NAME, BOT_TOKEN_CONFIGURATION_KEY, '1234567890')

    if not config.has_option(MAIN_SECTION_NAME, CHANNEL_ID_CONFIGURATION_KEY):
        config.set(MAIN_SECTION_NAME, CHANNEL_ID_CONFIGURATION_KEY, '-987654321')

    save_config()


def load_config():
    global bot_token
    global channel_id

    bot_token = config.get(MAIN_SECTION_NAME, BOT_TOKEN_CONFIGURATION_KEY)
    channel_id = config.get(MAIN_SECTION_NAME, CHANNEL_ID_CONFIGURATION_KEY)


def enable_api():
    global api
    api = fortnite_api.FortniteAPI()


def load_shop():
    global shop
    shop = api.shop.fetch(SHOP_LANGUAGE_DICTIONARY)


def enable_bot():
    bot.polling()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(CONFIGURATION_NAME)

    setup_config()
    load_config()

    enable_api()
    load_shop()

    # print(shop.daily.entries)

    bot = telebot.TeleBot(bot_token, parse_mode=None)
    print('Bot avviato')

    enable_bot()


