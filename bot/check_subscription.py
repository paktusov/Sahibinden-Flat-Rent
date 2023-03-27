import re

from storage.models.postgres.app import Ad
from storage.models.postgres.bot import Subscriber


def check_floor(ad: Ad, parameter: list[str]) -> bool:
    if "without_last" in parameter and ad.floor == str(ad.building_floor_count):
        return False
    if "without_first" in parameter and ad.floor in ["Elevation 1", "Garden-Floor"]:
        return False
    if "without_basement" in parameter and ad.floor in ["Basement", "Ground Floor", "Raised Ground Floor"]:
        return False
    return True


def check_rooms(ad: Ad, parameter: list[str]) -> bool:
    rooms_str = re.search(r"[0-9+]{1,3}", ad.room_count)[0]
    # sum rooms with all kitchen/dining room and minus 1 for kitchen/dining room
    rooms_count = sum(int(float(room)) for room in rooms_str.split("+")) - 1
    for param in parameter:
        if int(param) == rooms_count:
            return True
        if int(param) == 4 and rooms_count >= 4:
            return True
    return False


def check_heating(ad: Ad, parameter: list[str]) -> bool:
    heat_mapping = {
        "gas": {"Central Heating Boilers"},
        "electricity": {"Elektrikli Radyatör", "Room Heater"},
        "central": {"Central Heating", "Central Heating (Share Meter)"},
        "underfloor": {"Floor Heating"},
        "ac": {"Air Conditioning", "Fan Coil Unit", "VRV", "Heat Pump"},
    }
    for param in parameter:
        if ad.heating_type in heat_mapping[param]:
            return True
    return False


def check_furniture(ad: Ad, parameter: list) -> bool:
    if ad.furniture and "furnished" not in parameter:
        return False
    if not ad.furniture and "unfurnished" not in parameter:
        return False
    return True


def check_area(ad: Ad, parameter: dict) -> bool:
    if parameter[ad.address_town]:
        return True
    if parameter[ad.area]:
        return True
    return False


def check_max_price(ad: Ad, parameter: list[str]) -> bool:
    if ad.last_price > int(parameter[0]):
        return False
    return True


def subscription_validation(ad: Ad, subscriber: Subscriber) -> bool:
    check_functions = {
        "max_price": check_max_price,
        "floor": check_floor,
        "rooms": check_rooms,
        "heating": check_heating,
        "areas": check_area,
        "furniture": check_furniture,
    }
    return all(
        getattr(subscriber, key) in [None, "all"] or function(ad, getattr(subscriber, key))
        for key, function in check_functions.items()
    )
