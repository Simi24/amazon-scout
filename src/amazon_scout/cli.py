"""amazon-scout: search Amazon, read the review summary, build a cart link — through SerpApi.

  amazon-scout [--domain amazon.it] search "<query>" [--limit N] [--min-rating 4.5] [--organic] [--json]
  amazon-scout [--domain amazon.it] product <asin> [--json]
  amazon-scout [--domain amazon.it] cart <asin>[:qty] [<asin>[:qty] ...]
  amazon-scout credits
  amazon-scout setup [--key <key>] [--no-browser]

search and product cost one SerpApi search each (cached for 24 hours); cart, credits and setup are free.
The SerpApi key comes from SERPAPI_KEY or ~/.config/serpapi/key (written by `setup`, shared with other
SerpApi tools); the default domain from AMAZON_SCOUT_DOMAIN (amazon.com otherwise).
"""

import argparse
import sys

from amazon_scout import cart, key, render, serpapi


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--domain", help="Amazon domain, e.g. amazon.it, amazon.de, amazon.com")
    p.add_argument("--no-cache", action="store_true", help="ignore the 24-hour cache (costs a search)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search products (1 SerpApi search)")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--min-rating", type=float)
    s.add_argument("--organic", action="store_true", help="drop sponsored results")
    s.add_argument("--json", action="store_true")

    d = sub.add_parser("product", help="seller, stock and Amazon's review summary (1 SerpApi search)")
    d.add_argument("asin")
    d.add_argument("--json", action="store_true")

    c = sub.add_parser("cart", help="link that opens the cart already filled in (free)")
    c.add_argument("items", nargs="+", metavar="ASIN[:QTY]")

    sub.add_parser("credits", help="remaining SerpApi searches (free)")

    st = sub.add_parser("setup", help="save and check the SerpApi key (free)")
    st.add_argument("--key", help="the key, for non-interactive setup (otherwise it is asked without echo)")
    st.add_argument("--no-browser", action="store_true", help="do not open the SerpApi sign-up page")
    return p.parse_args()


def run(args: argparse.Namespace) -> str:
    use_cache = not args.no_cache
    match args.cmd:
        case "search":
            result = serpapi.filter_items(serpapi.search(args.query, args.domain, use_cache), args.limit, args.min_rating, args.organic)
            return result.model_dump_json(indent=1) if args.json else render.search(result)
        case "product":
            result = serpapi.product(args.asin, args.domain, use_cache)
            return result.model_dump_json(indent=1) if args.json else render.product(result)
        case "cart":
            return cart.cart_url(cart.parse_lines(args.items), serpapi.domain(args.domain))
        case "setup":
            return key.setup(args.key, open_browser=not args.no_browser)
        case _:
            return render.credits(serpapi.credits())


def main() -> None:
    args = parse_args()
    try:
        print(run(args))
    except (serpapi.MissingKeyError, serpapi.SerpApiError) as e:
        print(f"amazon-scout: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
