import logging

from storage import Storage

from app.get_data import get_areas
from app.models import Area


logger = logging.getLogger(__name__)

CLOSED_AREAS: list[str] = [
    "Hurma Mah.",
    "Sarısu Mh.",
    "Liman Mah.",
    "Topçular Mh.",
]


def import_areas() -> None:
    towns = Storage(table_name="towns").find_many()
    for town in towns:
        logger.info("Processing areas for %s", town["_id"])
        data = get_areas(town["_id"])
        if not data:
            logger.error("Can't parse areas from %s", town["_id"])
            continue
        for d in data:
            area = Area(town_id=town["_id"], **d)
            if Storage(table_name="areas").find_one({"_id": area.id}):
                continue
            if area.name in CLOSED_AREAS:
                area.is_closed = True
            Storage(table_name="areas").insert_one(area.dict(by_alias=True))


if __name__ == "__main__":
    import_areas()
