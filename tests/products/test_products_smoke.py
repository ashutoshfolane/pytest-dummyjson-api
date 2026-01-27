import pytest

from api_framework.clients.products_client import ProductsClient


@pytest.mark.smoke
def test_list_products_basic_shape(api):
    data = ProductsClient(api).list_products(limit=10, skip=0)

    assert isinstance(data.get("products"), list)
    assert data["limit"] == 10
    assert data["skip"] == 0
    assert data["total"] >= 1


@pytest.mark.smoke
def test_get_single_product(api):
    p = ProductsClient(api).get_product(1)

    assert p["id"] == 1
    assert "title" in p
    assert "price" in p


@pytest.mark.smoke
def test_add_product_simulated_crud(api):
    created = ProductsClient(api).add_product({"title": "BMW Pencil"})
    assert "id" in created
    assert created["title"] == "BMW Pencil"


@pytest.mark.smoke
def test_update_product_simulated_crud(api):
    updated = ProductsClient(api).update_product(1, {"title": "iPhone Galaxy +1"})
    assert updated["id"] == 1
    assert updated["title"] == "iPhone Galaxy +1"


@pytest.mark.smoke
def test_delete_product_simulated_crud(api):
    deleted = ProductsClient(api).delete_product(1)
    assert deleted["id"] == 1
    assert deleted["isDeleted"] is True
    assert "deletedOn" in deleted
