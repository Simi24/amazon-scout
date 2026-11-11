---
name: amazon-scout
description: Search Amazon, read Amazon's own review summary (per-topic positive/negative mentions) and build a link that opens the cart already filled in. Use it when the user wants to buy something on Amazon, compare Amazon options or prices (also against other stores), find a product's recurring defects, or prepare an order ("search amazon for", "how much is X on amazon", "is it cheaper on amazon?", "put it in the cart").
---

# amazon-scout

## Setup (only if the command is missing)

- `amazon-scout` not found: propose `uv tool install git+https://github.com/Simi24/amazon-scout` and wait for the person to agree.
- Exit code 2 with "missing SerpApi key": the person must create a free SerpApi account (250 searches a month) and run `amazon-scout setup` in their own terminal, which reads the key without echoing it and saves it to `~/.config/serpapi/key`. Never ask them to paste the key into the chat.
- Default store: set `AMAZON_SCOUT_DOMAIN` (e.g. `amazon.it`) or pass the option on each call.

## Commands

```bash
amazon-scout search "<query>" [--limit 10] [--min-rating 4.5] [--organic] [--json]   # 1 search
amazon-scout product <asin> [--json]                                                # 1 search
amazon-scout cart <asin>[:qty] [<asin>[:qty] ...]                                   # free
amazon-scout credits                                                                # free
```

## Budget

Every `search` and `product` call spends one SerpApi search (free plan: 250 a month, maybe shared with other tools). Answers are cached for 24 hours, so repeating a query is free.

- Run `credits` first when you plan more than a handful of calls.
- One `search` per item, then `product` only for the 1-2 finalists.
- Never use `--no-cache` unless the user asks for fresh prices.

## Recommended flow

1. `search` with a short query, usually with `--organic` (sponsored results are ads, not the best match).
2. `product <asin>` on the finalists: read the review summary and the topics with many **negative** mentions — those are the recurring defects. Check `sold by`: an unknown third-party seller is a risk compared with the brand's store or Amazon itself.
3. **Answer** with a comparison: price, rating and review count, recurring defects, delivery date, link.
4. If the user wants to buy, give them the `cart` link. **Never claim to have bought anything**: the link only fills the cart, the user reviews and pays.

## Reading the prices

- `old_price` is the strikethrough price, and it is **ambiguous**: on some EU deals it is the lowest price of the last 30 days (Omnibus directive), but it is often the launch list price (e.g. a robot vacuum at 499.99 "was 1499.99" whose recent street price was 700-750). Never judge a deal from it alone: for expensive items, search the web for the price history ("<product> minimo storico", "<product> lowest price") and other stores, or point the user to a tracker such as Keepa.
- `bought_last_month` ("400+ bought in past month") is a better popularity signal than the review count for recent listings.
- Multi-packs often rank next to single units: compare the price **per piece** before calling one option cheaper.
