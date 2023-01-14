import re

from app.models import Ad


def check_floor(ad: Ad, parameter: list[str]) -> bool:
    if "without_last" in parameter and ad.data.floor == str(ad.data.building_floor_count):
        return False
    if "without_first" in parameter and ad.data.floor in ["Elevation 1", "Garden-Floor"]:
        return False
    if "without_basement" in parameter and ad.data.floor in ["Basement", "Ground Floor", "Raised Ground Floor"]:
        return False
    return True


def check_rooms(ad: Ad, parameter: list[str]) -> bool:
    if "all" in parameter:
        return True
    rooms_str = re.search(r'[0-9+]{1,3}', ad.data.room_count)[0]
    # sum rooms with all kitchen/dining room and minus 1 for kitchen/dining room
    rooms = sum(int(float(room)) for room in rooms_str.split("+")) - 1
    for param in parameter:
        if int(param) == rooms:
            return True
        if param == 4 and rooms >= 4:
            return True
    return False


def check_heating(ad: Ad, parameter: list[str]) -> bool:
    if "all" in parameter:
        return True
    heat_mapping = {
        "gas": {"Central Heating Boilers"},
        "electricity": {"Elektrikli Radyatör", "Room Heater"},
        "central": {"Central Heating", "Central Heating (Share Meter)"},
        "underfloor": {"Floor Heating"},
        "ac": {"Air Conditioning", "Fan Coil Unit", "VRV", "Heat Pump"},
    }
    for param in parameter:
        if ad.data.heating_type in heat_mapping[param]:
            return True
    return False


def check_furniture(ad: Ad, parameter: list) -> bool:
    if ad.data.furniture and "furnished" not in parameter:
        return False
    if not ad.data.furniture and "unfurnished" not in parameter:
        return False
    return True


def check_area(ad: Ad, parameter: dict) -> bool:
    if parameter["all_" + ad.address_town]:
        return True
    if parameter[ad.data.area]:
        return True
    return False


# pylint: disable=too-many-return-statements)
def subscription_validation(ad: Ad, parameters: dict) -> bool:
    if not ad.data:
        return False
    if parameters.get("max_price") and ad.last_price > int(parameters["max_price"][0]):
        return False
    if parameters.get("floor") and not check_floor(ad, parameters["floor"]):
        return False
    if parameters.get("rooms") and not check_rooms(ad, parameters["rooms"]):
        return False
    if parameters.get("heating") and not check_heating(ad, parameters["heating"]):
        return False
    if parameters.get("furniture") and not check_furniture(ad, parameters["furniture"]):
        return False
    if parameters.get("areas") and not check_area(ad, parameters["areas"]):
        return False
    return True
