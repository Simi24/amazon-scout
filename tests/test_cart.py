import pytest

from amazon_scout.cart import cart_url, parse_lines


def test_cart_url() -> None:
    url = cart_url(parse_lines(["B0BYZP8NK2:4", "b0c1g7w72b"]), "amazon.it")
    assert url == "https://www.amazon.it/gp/aws/cart/add.html?ASIN.1=B0BYZP8NK2&Quantity.1=4&ASIN.2=B0C1G7W72B&Quantity.2=1"


def test_empty_cart() -> None:
    with pytest.raises(ValueError):
        cart_url([], "amazon.it")
