import json
from pathlib import Path

import pytest

from amazon_scout import serpapi

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def result():
    return serpapi.parse_search(json.loads((FIXTURES / "search.json").read_text(encoding="utf-8")), "sonoff snzb-02d", "amazon.it")


@pytest.fixture
def product():
    return serpapi.parse_product(json.loads((FIXTURES / "product.json").read_text(encoding="utf-8")), "amazon.it")


def test_sponsored_duplicate_keeps_organic(result) -> None:
    asins = [i.asin for i in result.items]
    assert len(asins) == len(set(asins))
    assert not next(i for i in result.items if i.asin == "B0FCG88WW6").sponsored


def test_item_fields(result) -> None:
    item = next(i for i in result.items if i.asin == "B0BYZP8NK2")
    assert item.price == 16.3
    assert item.rating == 4.4
    assert item.reviews == 3493
    assert item.url == "https://www.amazon.it/dp/B0BYZP8NK2/"


def test_old_price(result) -> None:
    assert next(i for i in result.items if i.asin == "B0FCG88WW6").old_price == 24.48


def test_filter_organic_and_limit(result) -> None:
    filtered = serpapi.filter_items(result, limit=2, organic_only=True)
    assert len(filtered.items) == 2
    assert not any(i.sponsored for i in filtered.items)


def test_product_seller_and_insights(product) -> None:
    assert product.item.asin == "B0BYZP8NK2"
    assert product.seller == "SONOFFEU"
    assert product.shipped_by == "Amazon"
    connectivity = next(i for i in product.insights if i.topic == "Connettività")
    assert connectivity.sentiment == "mixed"
    assert connectivity.negative == 32


def test_missing_key(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("SERPAPI_KEY", raising=False)
    monkeypatch.setattr(serpapi, "KEY_FILE", tmp_path / "missing")
    with pytest.raises(serpapi.MissingKeyError):
        serpapi.api_key()


def test_domain_from_env(monkeypatch) -> None:
    monkeypatch.setenv("AMAZON_SCOUT_DOMAIN", "amazon.de")
    assert serpapi.domain() == "amazon.de"
    assert serpapi.domain("amazon.it") == "amazon.it"
