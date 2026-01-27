import pytest

from api_framework.clients.products_client import ProductsClient


# -----------------------
# POSITIVE (regression)
# -----------------------
@pytest.mark.regression
def test_search_products_returns_list(api):
    data = ProductsClient(api).search_products(q="phone")

    assert isinstance(data.get("products"), list)
    assert data["total"] >= 0


@pytest.mark.regression
def test_list_categories(api):
    categories = ProductsClient(api).list_categories()

    assert isinstance(categories, list)
    assert len(categories) > 0
    assert all(isinstance(c, str) for c in categories)
    assert all(c.strip() for c in categories)


@pytest.mark.regression
def test_products_by_category(api):
    client = ProductsClient(api)
    category = client.list_categories()[0]  # slug str

    data = client.products_by_category(category)
    assert isinstance(data.get("products"), list)
    assert all(p.get("category") == category for p in data["products"])


@pytest.mark.regression
def test_list_products_pagination(api):
    client = ProductsClient(api)

    page1 = client.list_products(limit=5, skip=0)
    page2 = client.list_products(limit=5, skip=5)

    assert page1["products"][0]["id"] != page2["products"][0]["id"]


# -----------------------
# NEGATIVE (regression)
# -----------------------
@pytest.mark.regression
@pytest.mark.negative
def test_get_product_invalid_id_returns_404(api):
    r = api.get("/products/0")
    assert r.status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_products_by_category_invalid_returns_error_or_empty(api):
    r = api.get("/products/category/this-category-does-not-exist")

    if r.status_code in (404, 400):
        return

    assert r.status_code == 200
    body = r.json()
    assert "products" in body
    assert isinstance(body["products"], list)
    assert len(body["products"]) == 0


@pytest.mark.regression
@pytest.mark.negative
def test_search_products_empty_query_returns_200(api):
    # Not always an error in public APIs; validate behavior and shape.
    r = api.get("/products/search", params={"q": ""})
    assert r.status_code == 200
    body = r.json()
    assert "products" in body
