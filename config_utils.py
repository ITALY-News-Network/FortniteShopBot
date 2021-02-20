import os
import configparser

from process_images import generate_shop_image
from timer import Timer

TIMER_TIME_SECONDS = 60
MAIN_SECTION_NAME = 'GENERAL'
IS_ENABLED_CONFIGURATION_KEY = 'is_enabled'
BOT_TOKEN_CONFIGURATION_KEY = 'bot_token'
CHANNEL_ID_CONFIGURATION_KEY = 'channel_id'
MESSAGE_TO_SEND_CONFIGURATION_KEY = 'message_to_send'
TIMER_TIME_SECONDS_CONFIGURATION_NAME = 'timer_seconds'
CONFIGURATION_NAME = 'config.ini'
is_enabled = False
message_to_send = ''
bot_token = ''
channel_id = 0
creator_name = ''
config = None
api = None
shop = None
timer = None
stopFlag = None
LANGUAGE = 'it_IT'


def save_config():
    with open(CONFIGURATION_NAME, 'w') as configfile:
        config.write(configfile)


def default_config_value(key, value):
    if not config.has_option(MAIN_SECTION_NAME, key):
        config.set(MAIN_SECTION_NAME, key, value)


def setup_config():
    global config

    config = configparser.ConfigParser()
    config.read(CONFIGURATION_NAME)

    if not os.path.exists(CONFIGURATION_NAME):
        save_config()

    if not config.has_section(MAIN_SECTION_NAME):
        config.add_section(MAIN_SECTION_NAME)

    default_config_value(IS_ENABLED_CONFIGURATION_KEY, 'False')
    default_config_value(BOT_TOKEN_CONFIGURATION_KEY, '1234567890')
    default_config_value(CHANNEL_ID_CONFIGURATION_KEY, '-987654321')
    default_config_value(MESSAGE_TO_SEND_CONFIGURATION_KEY, 'Messaggio da inserire')
    default_config_value(TIMER_TIME_SECONDS_CONFIGURATION_NAME, '120')

    save_config()


def get_config_entry(key):
    return config.get(MAIN_SECTION_NAME, key)


def load_config():
    global bot_token
    global channel_id
    global is_enabled
    global message_to_send
    global creator_name
    global TIMER_TIME_SECONDS

    is_enabled = bool(get_config_entry(IS_ENABLED_CONFIGURATION_KEY) == 'True')
    bot_token = get_config_entry(BOT_TOKEN_CONFIGURATION_KEY)
    channel_id = get_config_entry(CHANNEL_ID_CONFIGURATION_KEY)
    message_to_send = get_config_entry(MESSAGE_TO_SEND_CONFIGURATION_KEY)
    TIMER_TIME_SECONDS = int(get_config_entry(TIMER_TIME_SECONDS_CONFIGURATION_NAME))

