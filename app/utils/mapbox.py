from config import mapbox_config


def get_map_image(lat: float, lon: float) -> str | None:
    if not lat or not lon:
        return None
    url = f"{mapbox_config.url}/pin-l+0031f5({lon},{lat})/{lon},{lat},12/1200x600?access_token={mapbox_config.token}"
    return url
