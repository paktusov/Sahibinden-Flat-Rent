import json
import logging
from random import shuffle

import requests
from curl_cffi import requests as requests_cffi
from pyquery import PyQuery

from app.models import AdDTO
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


class SahibindenClient:
    def __init__(
        self,
        host: str = SAHIBINDEN_HOST,
        session: requests_cffi.Session | requests.Session = requests_cffi.Session(impersonate="chrome110"),
    ):
        self.host = host
        self.host_ads_suffix = SAHIBINDEN_HOST_ADS_SUFFIX
        self.host_areas_suffix = SAHIBINDEN_HOST_AREAS_SUFFIX
        self.ads_default_params = SAHIBINDEN_ADS_DEFAULT_PARAMS
        self.ads_variable_params = SAHIBINDEN_ADS_VARIABLE_PARAMS
        self.timeout = 20
        # self.headers = HEADERS
        # self.cookies = COOKIES
        # self.impersonate = "chrome110"
        self.session = session
        # self.session.headers.update(self.headers)
        # self.session.cookies.update(self.cookies)
        self.session.timeout = self.timeout

    def get_status_code(self):
        try:
            response = self.session.get(self.host)
        except (requests_cffi.RequestsError, ConnectionError) as e:
            logger.error(e)
            return None
        return response.status_code

    def get_ads(self, parameters: dict) -> list[AdDTO | None]:
        try:
            response = self.session.get(
                url=self.host + self.host_ads_suffix,
                params=self.ads_default_params | self.ads_variable_params | parameters,
            )
        except (requests_cffi.RequestsError, ConnectionError) as e:
            logger.error(e)
            return []
        if response.status_code != 200:
            return []
        data = response.json()

        return [
            AdDTO(**fields, **parameters)
            for fields in data["classifiedMarkers"]
            if not (int(fields["id"]) < 1000000000 and not fields["thumbnailUrl"])
        ]

    def get_areas(self, town_code: str) -> list[dict] | None:
        try:
            response = self.session.get(
                url=self.host + self.host_areas_suffix,
                params={"townId": town_code},
            )
        except (requests_cffi.RequestsError, ConnectionError) as e:
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

    def get_data_and_photos_ad(self, url: str) -> (dict | None, list[str] | None):
        try:
            url_en = url.replace("ilan", "listing").replace("detay", "detail")
            response = self.session.get(url=self.host + url_en)
        except (requests_cffi.RequestsError, ConnectionError) as e:
            logger.error(e)
            return None, None
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
