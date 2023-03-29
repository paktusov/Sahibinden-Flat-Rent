import logging

from app.get_data import get_areas
from storage.connection.postgres import postgres_db
from storage.models.postgres.app import Area, Town


logger = logging.getLogger(__name__)

CLOSED_AREAS: list[str] = [
    "Hurma Mah.",
    "Sarısu Mh.",
    "Liman Mah.",
    "Topçular Mh.",
]


def import_areas() -> None:
    towns = postgres_db.query(Town).all()
    for town in towns:
        logger.info("Processing areas for %s", town.id)
        data = get_areas(town.id)
        if not data:
            logger.error("Can't parse areas from %s", town.id)
            continue
        for d in data:
            if postgres_db.query(Area).where(Area.id == d["id"]).first():
                continue
            area = Area(town_id=town.id, **d)
            if area.name in CLOSED_AREAS:
                area.is_closed = True
            postgres_db.add(area)
    postgres_db.commit()


if __name__ == "__main__":
    import_areas()
