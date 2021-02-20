import time
import requests
import json
import logging
from math import ceil
from sys import exit

import coloredlogs
from PIL import Image, ImageDraw

import config_utils
from config_utils import CONFIGURATION_NAME, setup_config, load_config, LANGUAGE
from util import ImageUtil, Utility

log = logging.getLogger(__name__)
item_shop_id = 0
image_saved_name = "itemshop.png"
logo_header_name = "header_shop.png"
logo_header_height = 210
logo_footer_height = 310
logo_footer_offset = 20
logo_footer_name = "footer_shop.png"
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")
IMAGE_LOAD_TYPE = "RGBA"
FEATURED_COLUMNS = 6
DAILY_COLUMNS = 3
CARD_WIDTH = 300
CARD_HEIGHT = 545
LEADING_OFFSET = 315
LEFT_OFFSET = 50
CARD_OFFSET = 10
SECTION_SPACING = 300
columns_length = 0
daily_length = 0
featured_length = 0
date = ""


class Athena:
    """Fortnite Item Shop Generator."""

    def main(self):
        initialized = Athena.LoadConfiguration(self)

        if initialized is True:
            itemShop = Utility.GET(
                self,
                "https://fortnite-api.com/shop/br",
                # {"x-api-key": self.apiKey},
                {"language": LANGUAGE}, )

            global date, item_shop_id
            itemShop = json.loads(itemShop)["data"]
            current_item_shop_id = itemShop["hash"]

            # Strip time from the timestamp, we only need the date
            current_date = Utility.ISOtoHuman(
                self, itemShop["date"].split("T")[0], LANGUAGE
            )

            date = current_date
            log.info(f"Retrieved Item Shop for {current_date}")

            if current_item_shop_id != item_shop_id:
                item_shop_id = current_item_shop_id
                self.sendImageToChannel(self, current_date, itemShop)
                # manda immagine
            else:
                log.info("Image not generated on this loop (same as previous)")

            log.info(f"End loop, waiting {config_utils.TIMER_TIME_SECONDS} seconds ------")
            log.info("<---->")

            time.sleep(config_utils.TIMER_TIME_SECONDS)
            Athena.main(Athena)

    def send_raw_photo(self, image_path, image_caption=""):
        data = {"chat_id": config_utils.channel_id, "caption": image_caption}
        url = "https://api.telegram.org/bot%s/sendPhoto" % config_utils.bot_token
        with open(image_path, "rb") as image_file:
            ret = requests.post(url, data=data, files={"photo": image_file})
        return ret.json()

    def sendImageToChannel(self, current_date, itemShop):
        shopImage = Athena.GenerateImage(self, current_date, itemShop)

        if config_utils.is_enabled:
            self.send_raw_photo(self, image_saved_name, config_utils.message_to_send.replace("{br}", "\n").replace("{DATE}", date))

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json

        Return True if configuration sucessfully loaded.
        """

        setup_config()
        load_config()

        try:
            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")

    def GenerateImage(self, date: str, itemShop: dict):
        """
        Generate the Item Shop image using the provided Item Shop.

        Return True if image sucessfully saved.
        """

        try:
            featured = itemShop["featured"]
            daily = itemShop["daily"]

            # Ensure both Featured and Daily have at least 1 item
            if (len(featured) <= 0) or (len(daily) <= 0):
                raise Exception(f"Featured: {len(featured)}, Daily: {len(daily)}")
        except Exception as e:
            log.critical(f"Failed to parse Item Shop Featured and Daily items, {e}")

            return False

        # Determine the max amount of rows required for the current
        # Item Shop when there are 3 columns for both Featured and Daily.
        # This allows us to determine the image height.
        featured_length = (FEATURED_COLUMNS * CARD_WIDTH) + ((FEATURED_COLUMNS - 1) * CARD_OFFSET)
        daily_length = (DAILY_COLUMNS * CARD_WIDTH) + ((DAILY_COLUMNS - 1) * CARD_OFFSET)
        columns_length = featured_length + daily_length
        rows = max(ceil(len(featured) / FEATURED_COLUMNS), ceil(len(daily) / DAILY_COLUMNS))
        shopImage = Image.new(IMAGE_LOAD_TYPE, (columns_length + SECTION_SPACING, ((CARD_HEIGHT * rows) + 340) + (
                rows - 1) * CARD_OFFSET + logo_footer_offset + logo_footer_height))

        try:
            background = ImageUtil.Open(self, "background.png")
            background = ImageUtil.RatioResize(
                self, background, shopImage.width, shopImage.height
            )
            shopImage.paste(
                background, ImageUtil.CenterX(self, background.width, shopImage.width)
            )
        except FileNotFoundError:
            log.warn("Failed to open background.png, defaulting to dark gray")
            shopImage.paste((18, 18, 18), [0, 0, shopImage.size[0], shopImage.size[1]])

        logo = ImageUtil.Open(self, logo_header_name)
        logo = ImageUtil.RatioResize(self, logo, 0, logo_header_height)
        shopImage.paste(
            logo, ImageUtil.CenterX(self, logo.width, shopImage.width, 20), logo
        )

        logo_footer = ImageUtil.Open(self, logo_footer_name)
        logo_footer = ImageUtil.RatioResize(self, logo_footer, 0, logo_footer_height)
        shopImage.paste(
            logo_footer,
            ImageUtil.CenterX(self, logo_footer.width, shopImage.width, shopImage.height - logo_footer.height - 20),
            logo_footer
        )

        canvas = ImageDraw.Draw(shopImage)
        font = ImageUtil.Font(self, 58)
        textWidth, _ = font.getsize(date.upper())
        canvas.text(
            ImageUtil.CenterX(self, textWidth, shopImage.width, 255),
            date,
            (255, 255, 255),
            font=font,
        )
        canvas.text((LEFT_OFFSET, 255), "IN EVIDENZA", (255, 255, 255), font=font)
        textWidth, _ = font.getsize("GIORNALIERO")
        canvas.text(
            (shopImage.width - (textWidth + LEFT_OFFSET), 255),
            "GIORNALIERO",
            (255, 255, 255),
            font=font,
        )

        # Track grid position
        i = 0

        for item in featured:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (LEFT_OFFSET + ((i % FEATURED_COLUMNS) * (card.width + CARD_OFFSET))),
                        (LEADING_OFFSET + ((i // FEATURED_COLUMNS) * (card.height + CARD_OFFSET))),
                    ),
                    card,
                )

                i += 1

        # Reset grid position
        i = 0
        DAILY_SPACING = SECTION_SPACING + featured_length - LEFT_OFFSET

        for item in daily:
            card = Athena.GenerateCard(self, item)

            if card is not None:
                shopImage.paste(
                    card,
                    (
                        (DAILY_SPACING + ((i % DAILY_COLUMNS) * (card.width + CARD_OFFSET))),
                        (LEADING_OFFSET + ((i // DAILY_COLUMNS) * (card.height + CARD_OFFSET))),
                    ),
                    card,
                )

                i += 1

        try:
            shopImage.save(image_saved_name)
            log.info("Generated Item Shop image")

            return True
        except Exception as e:
            log.critical(f"Failed to save Item Shop image, {e}")

    def GenerateCard(self, item: dict):
        """Return the card image for the provided Fortnite Item Shop item."""

        try:
            name = item["items"][0]["name"]
            rarity = item["items"][0]["rarity"]
            category = item["items"][0]["type"]
            price = item["finalPrice"]
            if isinstance(item["items"][0]["images"]["featured"], dict):
                icon = item["items"][0]["images"]["featured"]["url"]
            else:
                icon = item["items"][0]["images"]["icon"]["url"]
        except Exception as e:
            log.error(f"Failed to parse item {name}, {e}")

            return

        if rarity == "frozen":
            blendColor = (148, 223, 255)
        elif rarity == "lava":
            blendColor = (234, 141, 35)
        elif rarity == "legendary":
            blendColor = (211, 120, 65)
        elif rarity == "dark":
            blendColor = (251, 34, 223)
        elif rarity == "starwars":
            blendColor = (231, 196, 19)
        elif rarity == "marvel":
            blendColor = (197, 51, 52)
        elif rarity == "dc":
            blendColor = (84, 117, 199)
        elif rarity == "icon":
            blendColor = (54, 183, 183)
        elif rarity == "shadow":
            blendColor = (113, 113, 113)
        elif rarity == "epic":
            blendColor = (177, 91, 226)
        elif rarity == "rare":
            blendColor = (73, 172, 242)
        elif rarity == "uncommon":
            blendColor = (96, 170, 58)
        elif rarity == "common":
            blendColor = (190, 190, 190)
        else:
            blendColor = (255, 255, 255)

        card = Image.new(IMAGE_LOAD_TYPE, (CARD_WIDTH, CARD_HEIGHT))

        try:
            layer = ImageUtil.Open(self, f"card_top_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open card_top_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, "card_top_common.png")

        card.paste(layer)

        icon = ImageUtil.Download(self, icon)
        if (category == "outfit") or (category == "emote"):
            icon = ImageUtil.RatioResize(self, icon, 285, 365)
        elif category == "wrap":
            icon = ImageUtil.RatioResize(self, icon, 230, 310)
        else:
            icon = ImageUtil.RatioResize(self, icon, 310, 390)
        if (category == "outfit") or (category == "emote"):
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width), icon)
        else:
            card.paste(icon, ImageUtil.CenterX(self, icon.width, card.width, 15), icon)

        if len(item["items"]) > 1:
            # Track grid position
            i = 0

            # Start at position 1 in items array
            for extra in item["items"][1:]:
                try:
                    extraRarity = extra["rarity"]
                    extraIcon = extra["images"]["smallIcon"]["url"]
                except Exception as e:
                    log.error(f"Failed to parse item {name}, {e}")

                    return

                try:
                    layer = ImageUtil.Open(self, f"box_bottom_{extraRarity}.png")
                except FileNotFoundError:
                    log.warn(
                        f"Failed to open box_bottom_{extraRarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil.Open(self, "box_bottom_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (layer.height))),
                    ),
                )

                extraIcon = ImageUtil.Download(self, extraIcon)
                extraIcon = ImageUtil.RatioResize(self, extraIcon, 75, 75)

                card.paste(
                    extraIcon,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (extraIcon.height))),
                    ),
                    extraIcon,
                )

                try:
                    layer = ImageUtil.Open(self, f"box_faceplate_{extraRarity}.png")
                except FileNotFoundError:
                    log.warn(
                        f"Failed to open box_faceplate_{extraRarity}.png, defaulted to Common"
                    )
                    layer = ImageUtil.Open(self, "box_faceplate_common.png")

                card.paste(
                    layer,
                    (
                        (card.width - (layer.width + 9)),
                        (9 + ((i // 1) * (layer.height))),
                    ),
                    layer,
                )

                i += 1

        try:
            layer = ImageUtil.Open(self, f"card_faceplate_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open card_faceplate_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, "card_faceplate_common.png")

        card.paste(layer, layer)

        try:
            layer = ImageUtil.Open(self, f"card_bottom_{rarity}.png")
        except FileNotFoundError:
            log.warn(f"Failed to open card_bottom_{rarity}.png, defaulted to Common")
            layer = ImageUtil.Open(self, "card_bottom_common.png")

        card.paste(layer, layer)

        canvas = ImageDraw.Draw(card)

        font = ImageUtil.Font(self, 30)
        textWidth, _ = font.getsize(f"{rarity.capitalize()} {category.capitalize()}")
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, 385),
            f"{rarity.capitalize()} {category.capitalize()}",
            blendColor,
            font=font,
        )

        vbucks = ImageUtil.Open(self, "vbucks.png")
        vbucks = ImageUtil.RatioResize(self, vbucks, 25, 25)

        price = str(f"{price:,}")
        textWidth, _ = font.getsize(price)
        canvas.text(
            ImageUtil.CenterX(self, ((textWidth - 5) - vbucks.width), card.width, 495),
            price,
            blendColor,
            font=font,
        )

        card.paste(
            vbucks,
            ImageUtil.CenterX(self, (vbucks.width + (textWidth + 5)), card.width, 495),
            vbucks,
        )

        font = ImageUtil.Font(self, 56)
        textWidth, _ = font.getsize(name)
        change = 0
        if textWidth >= 270:
            # Ensure that the item name does not overflow
            font, textWidth, change = ImageUtil.FitTextX(self, name, 56, 260)
        canvas.text(
            ImageUtil.CenterX(self, textWidth, card.width, (425 + (change / 2))),
            name,
            (255, 255, 255),
            font=font,
        )

        return card


if __name__ == "__main__":
    try:
        Athena.main(Athena)
    except KeyboardInterrupt:
        log.info("Exiting...")
        exit()
