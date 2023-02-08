import logging

from storage.connection.postgres import db
from storage.models import Area, Town

from app.get_data import get_areas


logger = logging.getLogger(__name__)

CLOSED_AREAS: list[str] = [
    "Hurma Mah.",
    "Sarısu Mh.",
    "Liman Mah.",
    "Topçular Mh.",
]


def import_areas() -> None:
    towns = db.query(Town).all()
    for town in towns:
        logger.info("Processing areas for %s", town.id)
        data = get_areas(town.id)
        if not data:
            logger.error("Can't parse areas from %s", town.id)
            continue
        for d in data:
            if db.query(Area).where(Area.id == d["id"]).first():
                continue
            area = Area(town_id=town.id, **d)
            if area.name in CLOSED_AREAS:
                area.is_closed = True
            db.add(area)
    db.commit()


if __name__ == "__main__":
    import_areas()
