import pytest
import requests

from app.get_data import SahibindenClient


@pytest.fixture
def client() -> SahibindenClient:
    """
    Transfer requests instead requests_cffi for mock
    """
    test_session = requests.Session()
    test_client = SahibindenClient(session=test_session)
    return test_client
