"""Amazon through SerpApi (engines `amazon` and `amazon_product`).

Amazon blocks direct automated access; SerpApi serves the same pages as structured JSON. Every new call
costs one search from the monthly quota (250 on the free plan): answers are cached for a day.
"""

import os
import urllib.parse
from pathlib import Path

from amazon_scout import http
from amazon_scout.models import Credits, Item, Product, ReviewInsight, SearchResult

ENDPOINT = "https://serpapi.com/search.json"
ACCOUNT_ENDPOINT = "https://serpapi.com/account.json"
KEY_FILE = Path.home() / ".config" / "amazon-scout" / "serpapi_key"
DEFAULT_DOMAIN = "amazon.com"
LANGUAGES = {"amazon.it": "it_IT", "amazon.de": "de_DE", "amazon.fr": "fr_FR", "amazon.es": "es_ES", "amazon.co.uk": "en_GB"}


class MissingKeyError(RuntimeError):
    """No SerpApi key: set SERPAPI_KEY or write it to ~/.config/amazon-scout/serpapi_key."""


class SerpApiError(RuntimeError):
    """SerpApi answered with an error (quota exhausted, invalid key, unknown ASIN...)."""


def api_key() -> str:
    key = os.environ.get("SERPAPI_KEY") or (KEY_FILE.read_text().strip() if KEY_FILE.exists() else "")
    if not key:
        raise MissingKeyError(f"missing SerpApi key: set SERPAPI_KEY or write it to {KEY_FILE}")
    return key


def domain(name: str | None = None) -> str:
    return name or os.environ.get("AMAZON_SCOUT_DOMAIN", DEFAULT_DOMAIN)


def _fetch(params: dict[str, str], use_cache: bool) -> dict:
    query = {**params, **({"language": LANGUAGES[params["amazon_domain"]]} if params["amazon_domain"] in LANGUAGES else {})}
    cache_key = f"{ENDPOINT}?{urllib.parse.urlencode(query)}"
    payload = http.get_json(f"{cache_key}&{urllib.parse.urlencode({'api_key': api_key()})}", cache_key, use_cache)
    if payload.get("error"):
        raise SerpApiError(payload["error"])
    return payload


def parse_item(raw: dict, amazon_domain: str) -> Item:
    asin = raw.get("asin", "")
    return Item(
        asin=asin,
        title=raw.get("title", ""),
        url=f"https://www.{amazon_domain}/dp/{asin}/",
        price=raw.get("extracted_price"),
        old_price=raw.get("extracted_old_price"),
        rating=raw.get("rating"),
        reviews=raw.get("reviews"),
        bought_last_month=raw.get("bought_last_month"),
        sponsored=bool(raw.get("sponsored")),
        delivery=raw.get("delivery") or [],
    )


def parse_search(payload: dict, query: str, amazon_domain: str) -> SearchResult:
    items: dict[str, Item] = {}
    for raw in payload.get("organic_results") or []:
        if not raw.get("asin"):
            continue
        item = parse_item(raw, amazon_domain)
        # a sponsored product can show up again among the organic results: keep the organic one
        if item.asin not in items or (items[item.asin].sponsored and not item.sponsored):
            items[item.asin] = item
    return SearchResult(query=query, domain=amazon_domain, items=list(items.values()))


def _feature(features: dict, *names: str) -> str | None:
    """Seller and shipper labels are localized ('venditore', 'sold by'...): take the first one present."""
    return next(((features.get(n) or {}).get("text") for n in names if features.get(n)), None)


def parse_product(payload: dict, amazon_domain: str) -> Product:
    features = ((payload.get("purchase_options") or {}).get("single_offer") or {}).get("features") or {}
    summary = (payload.get("reviews_information") or {}).get("summary") or {}
    raw = payload.get("product_results") or {}
    return Product(
        item=parse_item(raw, amazon_domain),
        stock=raw.get("stock"),
        seller=_feature(features, "sold_by", "venditore", "verkäufer", "vendeur", "vendido_por"),
        shipped_by=_feature(features, "ships_from", "spedizione", "versand", "expédition", "envío"),
        review_summary=summary.get("text"),
        insights=[
            ReviewInsight(
                topic=i.get("title", ""),
                sentiment=i.get("sentiment", ""),
                positive=(i.get("mentions") or {}).get("positive", 0),
                negative=(i.get("mentions") or {}).get("negative", 0),
                summary=i.get("summary", ""),
            )
            for i in summary.get("insights") or []
        ],
    )


def search(query: str, amazon_domain: str | None = None, use_cache: bool = True) -> SearchResult:
    d = domain(amazon_domain)
    return parse_search(_fetch({"engine": "amazon", "amazon_domain": d, "k": query}, use_cache), query, d)


def product(asin: str, amazon_domain: str | None = None, use_cache: bool = True) -> Product:
    d = domain(amazon_domain)
    return parse_product(_fetch({"engine": "amazon_product", "amazon_domain": d, "asin": asin}, use_cache), d)


def credits() -> Credits:
    """Remaining quota. The account endpoint does not consume searches."""
    payload = http.get_json(f"{ACCOUNT_ENDPOINT}?{urllib.parse.urlencode({'api_key': api_key()})}", use_cache=False)
    if payload.get("error"):
        raise SerpApiError(payload["error"])
    return Credits(
        plan=payload.get("plan_name"), searches_left=payload.get("total_searches_left"), used_this_month=payload.get("this_month_usage")
    )


def filter_items(result: SearchResult, limit: int, min_rating: float | None = None, organic_only: bool = False) -> SearchResult:
    items = [i for i in result.items if (min_rating is None or (i.rating or 0) >= min_rating) and not (organic_only and i.sponsored)]
    return result.model_copy(update={"items": items[:limit]})
