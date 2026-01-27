import pytest

from api_framework.clients.carts_client import CartsClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
def test_list_carts_returns_shape(api):
    data = CartsClient(api).list_carts(limit=10, skip=0)

    assert "carts" in data
    assert isinstance(data["carts"], list)
    assert "total" in data
    assert isinstance(data["total"], int)


@pytest.mark.regression
def test_get_cart_by_id(api):
    cart = CartsClient(api).get_cart(1)
    assert cart["id"] == 1
    assert "products" in cart
    assert isinstance(cart["products"], list)


@pytest.mark.regression
def test_carts_pagination(api):
    client = CartsClient(api)
    page1 = client.list_carts(limit=5, skip=0)
    page2 = client.list_carts(limit=5, skip=5)

    assert page1["carts"][0]["id"] != page2["carts"][0]["id"]


@pytest.mark.regression
def test_carts_by_user(api):
    data = CartsClient(api).carts_by_user(1)
    assert isinstance(data.get("carts"), list)
    if data["carts"]:
        assert all(c.get("userId") == 1 for c in data["carts"])


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.negative
@pytest.mark.regression
def test_get_cart_invalid_id_returns_404_or_error(api):
    r = CartsClient(api).get_cart_raw(0)
    assert r.status_code in (404, 400)


@pytest.mark.negative
@pytest.mark.regression
def test_carts_by_user_invalid_returns_404_or_empty(api):
    r = CartsClient(api).carts_by_user_raw(0)

    if r.status_code in (404, 400):
        return

    # Some public APIs return 200 + empty lists for unknown user IDs
    assert r.status_code == 200
    body = r.json()
    assert "carts" in body
    assert isinstance(body["carts"], list)
