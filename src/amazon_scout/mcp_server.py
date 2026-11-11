"""MCP server (stdio) on top of the same functions as the CLI. Needs the extra: uv sync --extra mcp."""

from fastmcp import FastMCP

from amazon_scout import cart, serpapi
from amazon_scout.models import CartLine, Credits, Product, SearchResult

mcp = FastMCP("amazon-scout")


@mcp.tool
def search_products(
    query: str, limit: int = 10, min_rating: float | None = None, organic_only: bool = False, domain: str | None = None
) -> SearchResult:
    """Search Amazon (costs one SerpApi search, cached 24h). Returns price, strikethrough price, rating, review count,
    'bought last month' and delivery. domain: e.g. amazon.it, amazon.de, amazon.com."""
    return serpapi.filter_items(serpapi.search(query, domain), limit, min_rating, organic_only)


@mcp.tool
def product_details(asin: str, domain: str | None = None) -> Product:
    """Seller, shipper, stock and Amazon's AI review summary with per-topic positive/negative mention counts
    (costs one SerpApi search). Topics with many negative mentions are the recurring defects."""
    return serpapi.product(asin, domain)


@mcp.tool
def cart_link(lines: list[CartLine], domain: str | None = None) -> str:
    """Link that opens the Amazon cart already filled in. The person reviews and pays: nothing is bought automatically."""
    return cart.cart_url(lines, serpapi.domain(domain))


@mcp.tool
def remaining_credits() -> Credits:
    """Remaining SerpApi searches this month (free call)."""
    return serpapi.credits()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
