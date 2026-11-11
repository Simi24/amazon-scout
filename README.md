# amazon-scout

Search Amazon, read Amazon's own review summary and build a link that opens a ready-to-checkout cart — built to be driven by an LLM agent. It ships as a CLI with compact text or JSON output, an agent skill, and an optional MCP server.

```text
$ amazon-scout --domain amazon.it product B0BYZP8NK2
- [B0BYZP8NK2] SONOFF SNZB-02D Zigbee temperature and humidity sensor ...
    16.30 · ★4.4 · 3493 reviews · 400+ bought in past month
    In stock · sold by SONOFFEU · shipped by Amazon
- Connectivity [mixed] +25/-32: customers have mixed opinions about connectivity ...
- Battery life [mixed] +12/-14: ...
```

## How it works

Amazon blocks direct automated access and its affiliate API (now the Creators API) requires an active Associates account with recent sales. amazon-scout uses [SerpApi](https://serpapi.com/) instead, which returns Amazon search results and product pages as JSON.

- **Search**: price, strikethrough price, rating, review count, "bought last month", delivery, sponsored flag (sponsored duplicates are folded into the organic result).
- **Product**: seller, shipper, stock, and Amazon's AI review summary with positive/negative mention counts per topic — the topics with many negative mentions are the recurring defects.
- **Cart link**: Amazon's documented "add to cart" form URL (`/gp/aws/cart/add.html?ASIN.1=…&Quantity.1=…`) opens the cart already filled in. The agent prepares the order, the person checks out. Nothing is bought automatically.
- **Quota**: each search or product call costs one SerpApi search (250 a month on the free plan). Answers are cached on disk for 24 hours (`~/.cache/amazon-scout`, or `AMAZON_SCOUT_CACHE`); the cache key never contains the API key. `credits` shows what is left without spending anything.

No price history: SerpApi returns the current price only. Use a tracker such as Keepa for that.

## Install

```bash
uv tool install git+https://github.com/Simi24/amazon-scout
mkdir -p ~/.config/amazon-scout && echo "<your SerpApi key>" > ~/.config/amazon-scout/serpapi_key
chmod 600 ~/.config/amazon-scout/serpapi_key
export AMAZON_SCOUT_DOMAIN=amazon.it   # optional, defaults to amazon.com
```

`SERPAPI_KEY` in the environment works too.

## Usage

```bash
amazon-scout search "zigbee door sensor" --organic --min-rating 4.3 --limit 5
amazon-scout product B0BYZP8NK2
amazon-scout cart B0BYZP8NK2:4 B0C1G7W72B
amazon-scout credits
```

## Agent skill

`skills/amazon-scout/SKILL.md` tells an agent when to use the tool, how to spend the quota and how to read the results. For Claude Code:

```bash
git clone https://github.com/Simi24/amazon-scout
ln -s "$PWD/amazon-scout/skills/amazon-scout" ~/.claude/skills/amazon-scout
```

It pairs well with [ali-scout](https://github.com/Simi24/ali-scout): load both skills and ask the agent where to buy.

## MCP server (optional)

```bash
uv tool install "amazon-scout[mcp] @ git+https://github.com/Simi24/amazon-scout"
```

```json
{
  "mcpServers": {
    "amazon-scout": { "command": "amazon-scout-mcp", "env": { "AMAZON_SCOUT_DOMAIN": "amazon.it" } }
  }
}
```

Tools: `search_products`, `product_details`, `cart_link`, `remaining_credits`.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format .
```

Tests run offline against saved fixtures in `tests/fixtures/`.

## Disclaimer

Not affiliated with Amazon or SerpApi. Product data comes from SerpApi under its terms of service.

## License

MIT
