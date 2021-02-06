from fortnite_api import BrShop


def generate_shop_image(shop: BrShop):
    for entry in shop.special_featured.entries:
        print(entry.items[0].)