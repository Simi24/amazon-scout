"""Compact text output, readable by a person and by an LLM without wasting tokens."""

from amazon_scout.models import Credits, Item, Product, SearchResult


def item(i: Item) -> str:
    price = f"{i.price:.2f}" if i.price is not None else "price n/a"
    strike = f" (was {i.old_price:.2f}, -{(1 - i.price / i.old_price) * 100:.0f}%)" if i.old_price and i.price else ""
    stats = " · ".join(
        s for s in [f"★{i.rating}" if i.rating else "", f"{i.reviews} reviews" if i.reviews else "", i.bought_last_month or ""] if s
    )
    sponsored = " [sponsored]" if i.sponsored else ""
    delivery = f"\n    {i.delivery[0]}" if i.delivery else ""
    return f"- [{i.asin}] {i.title}{sponsored}\n    {price}{strike} · {stats}\n    {i.url}{delivery}"


def search(r: SearchResult) -> str:
    return "\n".join([f"{r.domain} '{r.query}'", *(item(i) for i in r.items)])


def product(p: Product) -> str:
    lines = [item(p.item)]
    offer = [p.stock or "", f"sold by {p.seller}" if p.seller else "", f"shipped by {p.shipped_by}" if p.shipped_by else ""]
    if any(offer):
        lines.append("    " + " · ".join(s for s in offer if s))
    if p.review_summary:
        lines.append(f"Review summary (by Amazon): {p.review_summary}")
    for ins in p.insights:
        lines.append(f"- {ins.topic} [{ins.sentiment}] +{ins.positive}/-{ins.negative}: {ins.summary}")
    return "\n".join(lines)


def credits(c: Credits) -> str:
    return f"SerpApi {c.plan}: {c.searches_left} searches left ({c.used_this_month} used this month)"
