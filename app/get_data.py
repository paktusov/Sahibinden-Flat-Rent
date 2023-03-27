import json
import logging
from random import shuffle

import requests
from curl_cffi import requests as requests_cffi
from pyquery import PyQuery

from app.models import AdDTO
from config import mapbox_config
from storage.connection.postgres import postgres_db
from storage.models.postgres.app import Cookie, Header


logger = logging.getLogger(__name__)

SAHIBINDEN_HOST = "https://secure.sahibinden.com"
SAHIBINDEN_HOST_ADS_SUFFIX = "/ajax/mapSearch/classified/markers"
SAHIBINDEN_HOST_AREAS_SUFFIX = "/ajax/location/getDistricts"
SAHIBINDEN_ADS_DEFAULT_PARAMS = {
    "m:includeProjectSummaryFields": "true",
    "language": "en",
    "category": "16624",
    "address_country": "1",
    "price_currency": "1",
    "address_city": "7",
    "pagingOffset": "0",
}
SAHIBINDEN_ADS_VARIABLE_PARAMS = {
    # (1day, 7days, 15days, 30days)
    "price_max": "25000",
    "date": "30days",
}
HEADERS = postgres_db.query(Header).first().data
COOKIES = postgres_db.query(Cookie).first().data


def get_ads(parameters: dict) -> list[AdDTO] | None:
    try:
        response = requests_cffi.get(
            url=SAHIBINDEN_HOST + SAHIBINDEN_HOST_ADS_SUFFIX,
            params=SAHIBINDEN_ADS_DEFAULT_PARAMS | SAHIBINDEN_ADS_VARIABLE_PARAMS | parameters,
            cookies=COOKIES,
            headers=HEADERS,
            timeout=10,
            impersonate="chrome101",
        )
    except requests_cffi.RequestsError as e:
        logger.error(e)
        return None

    if response.status_code != 200:
        return []
    data = response.json()

    return [
        AdDTO(**fields, **parameters)
        for fields in data["classifiedMarkers"]
        if not (int(fields["id"]) < 1000000000 and not fields["thumbnailUrl"])
    ]


def get_areas(town_code: str) -> list[dict] | None:
    try:
        response = requests_cffi.get(
            url=SAHIBINDEN_HOST + SAHIBINDEN_HOST_AREAS_SUFFIX,
            params={"townId": town_code},
            cookies=COOKIES,
            headers=HEADERS,
            timeout=10,
            impersonate="chrome101",
        )
    except requests_cffi.RequestsError as e:
        logger.error(e)
        return None

    if response.status_code != 200:
        return None
    areas = []
    for neighbourhood in response.json():
        for area in neighbourhood["quarters"]:
            if not isinstance(area, dict):
                continue
            areas.append(area)
    return areas


def get_data_and_photos_ad(url: str) -> (dict | None, list[str] | None):
    response = requests.get(url=url, cookies=COOKIES, headers=HEADERS, timeout=10)
    if response.status_code != 200:
        return None, None

    html = PyQuery(response.text)
    custom_data = html("#gaPageViewTrackingJson").attr("data-json")
    if not custom_data:
        return None, None
    data = {i["name"]: i["value"] for i in json.loads(custom_data)["customVars"]}

    img_links = []
    available_mega_photos = "passive" not in html('a:Contains("Mega Photo")').attr("class")
    if available_mega_photos:
        for div in html("div.megaPhotoThmbItem"):
            link = PyQuery(div).find("img").attr("data-source")
            if link:
                img_links.append(link)
    else:
        for img in html("div.classifiedDetailMainPhoto").find("img"):
            link = PyQuery(img).attr("data-src")
            if link:
                img_links.append(link)
    shuffle(img_links)
    return data, img_links[:3]


def get_map_image(lat: float, lon: float) -> str | None:
    if not lat or not lon:
        return None
    url = f"{mapbox_config.url}/pin-l+0031f5({lon},{lat})/{lon},{lat},12/1200x600?access_token={mapbox_config.token}"
    return url
