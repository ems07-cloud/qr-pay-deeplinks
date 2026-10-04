from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from main import app
from tests.test_gost_parser import VALID

client = TestClient(app)


def test_deeplink_contains_payment_details():
    resp = client.post("/api/v1/deeplink", json={"bank": "Sber", "os": "IOS", "gost": VALID})
    assert resp.status_code == 200
    (link,) = resp.json()["links"]
    parts = urlsplit(link)
    assert parts.scheme == "test-sber-ios"
    query = parse_qs(parts.query)
    assert query["account"] == ["40702810900000012345"]
    assert query["sum"] == ["1500"]
    assert query["purpose"] == ["Оплата по счёту 42"]


@pytest.mark.parametrize(
    "payload, detail",
    [
        ({"bank": "unknownbank", "os": "ios", "gost": VALID}, "Неподдерживаемый банк"),
        ({"bank": "sber", "os": "windows", "gost": VALID}, "Неподдерживаемая ОС"),
        ({"bank": "sber", "os": "ios", "gost": "ST00012|Name=x"}, "Отсутствуют обязательные поля"),
    ],
    ids=["unknown-bank", "unknown-os", "missing-fields"],
)
def test_deeplink_rejects_bad_input(payload, detail):
    resp = client.post("/api/v1/deeplink", json=payload)
    assert resp.status_code == 400
    assert detail in resp.json()["detail"]


def test_get_links_for_invoice():
    resp = client.get("/api/v1/get_links", params={"bank": "alfa", "os": "android", "invoice": "INV-7"})
    assert resp.status_code == 200
    assert resp.json()["links"] == ["test-alfa-android://pay?invoice=INV-7"]


def test_pages_are_served():
    assert client.get("/choose-bank/INV-7").status_code == 200
    assert client.get("/open/vtb/INV-7").status_code == 200
    assert client.get("/open/nobank/INV-7").status_code == 400
