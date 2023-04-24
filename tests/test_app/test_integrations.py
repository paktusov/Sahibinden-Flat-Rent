import random

import requests
from starlette import status

from app.utils.mapbox import get_map_image


class TestMapBox:
    def test_get_map_image(self):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        receive_map_image_url = get_map_image(lat, lon)
        response = requests.get(receive_map_image_url, timeout=20)
        assert response.status_code == status.HTTP_200_OK
