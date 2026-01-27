import pytest

from api_framework.clients.carts_client import CartsClient


@pytest.mark.smoke
def test_add_cart_smoke(api):
    client = CartsClient(api)

    payload = {
        "userId": 1,
        "products": [
            {"id": 1, "quantity": 1},
            {"id": 2, "quantity": 2},
        ],
    }

    data = client.add_cart(payload)

    # DummyJSON typically returns a cart-like object
    assert "id" in data
    assert data.get("userId") == 1
    assert isinstance(data.get("products"), list)
    assert len(data["products"]) > 0


@pytest.mark.smoke
def test_update_cart_smoke(api):
    client = CartsClient(api)

    # Use an existing cart id for “safe” update in a public demo API
    cart_id = 1

    payload = {
        "products": [
            {"id": 1, "quantity": 3},
        ]
    }

    data = client.update_cart(cart_id, payload)

    assert data.get("id") == cart_id
    assert isinstance(data.get("products"), list)
    assert any(p.get("id") == 1 for p in data["products"])


@pytest.mark.smoke
def test_delete_cart_smoke(api):
    client = CartsClient(api)

    cart_id = 1
    data = client.delete_cart(cart_id)

    assert data.get("id") == cart_id
    # DummyJSON often returns {"isDeleted": true, ...}
    assert data.get("isDeleted") is True or "isDeleted" in data


@pytest.mark.smoke
def test_list_carts_smoke(api):
    data = CartsClient(api).list_carts(limit=5, skip=0)
    assert isinstance(data.get("carts"), list)
    assert data.get("limit") == 5


@pytest.mark.smoke
def test_get_cart_smoke(api):
    cart = CartsClient(api).get_cart(1)
    assert cart["id"] == 1
    assert isinstance(cart.get("products"), list)
