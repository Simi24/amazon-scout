"""Cart links: Amazon's documented "add to cart" form URL opens the cart already filled in.

The agent picks the products, the person opens the link and checks out. Nothing is bought automatically.
"""

import urllib.parse

from amazon_scout.models import CartLine


def cart_url(lines: list[CartLine], amazon_domain: str) -> str:
    if not lines:
        raise ValueError("an empty cart has no link")
    params: dict[str, str | int] = {}
    for n, line in enumerate(lines, start=1):
        params[f"ASIN.{n}"] = line.asin
        params[f"Quantity.{n}"] = line.quantity
    return f"https://www.{amazon_domain}/gp/aws/cart/add.html?{urllib.parse.urlencode(params)}"


def parse_lines(specs: list[str]) -> list[CartLine]:
    """'B0BYZP8NK2' or 'B0BYZP8NK2:4' -> CartLine."""
    lines = []
    for spec in specs:
        asin, _, qty = spec.partition(":")
        lines.append(CartLine(asin=asin.strip().upper(), quantity=int(qty) if qty else 1))
    return lines
