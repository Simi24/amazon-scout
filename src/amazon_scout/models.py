"""Models returned by amazon-scout: they are also the JSON contract for agents."""

from pydantic import BaseModel


class Item(BaseModel):
    asin: str
    title: str
    url: str
    price: float | None
    old_price: float | None  # strikethrough price: the 30-day low on EU deals, or a list price elsewhere
    rating: float | None
    reviews: int | None
    bought_last_month: str | None
    sponsored: bool
    delivery: list[str]


class SearchResult(BaseModel):
    query: str
    domain: str
    items: list[Item]


class ReviewInsight(BaseModel):
    topic: str
    sentiment: str  # positive / negative / mixed
    positive: int
    negative: int
    summary: str


class Product(BaseModel):
    item: Item
    stock: str | None
    seller: str | None
    shipped_by: str | None
    review_summary: str | None  # Amazon's own AI summary of the reviews
    insights: list[ReviewInsight]


class CartLine(BaseModel):
    asin: str
    quantity: int = 1


class Credits(BaseModel):
    plan: str | None
    searches_left: int | None
    used_this_month: int | None
