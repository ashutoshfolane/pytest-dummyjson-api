import pytest

from api_framework.clients.recipes_client import RecipesClient

# -----------------------
# POSITIVE (regression)
# -----------------------


@pytest.mark.regression
def test_search_recipes_returns_list(api):
    data = RecipesClient(api).search_recipes(q="chicken")

    assert isinstance(data.get("recipes"), list)
    assert data.get("total", 0) >= 0


@pytest.mark.regression
def test_list_recipes_pagination(api):
    client = RecipesClient(api)

    page1 = client.list_recipes(limit=5, skip=0)
    page2 = client.list_recipes(limit=5, skip=5)

    assert page1["recipes"][0]["id"] != page2["recipes"][0]["id"]


@pytest.mark.regression
def test_list_tags_returns_list(api):
    tags = RecipesClient(api).list_tags()

    assert isinstance(tags, list)
    assert len(tags) > 0


@pytest.mark.regression
def test_recipes_by_tag(api):
    client = RecipesClient(api)
    tags = client.list_tags()

    # tags can be list[str] or list[dict] depending on API evolution; normalize to str
    t0 = tags[0]
    tag = t0["name"] if isinstance(t0, dict) and "name" in t0 else str(t0)

    data = client.recipes_by_tag(tag)
    assert isinstance(data.get("recipes"), list)


@pytest.mark.regression
def test_recipes_by_meal_type(api):
    # Use a common meal-type likely to exist; if API evolves, this still validates behavior.
    data = RecipesClient(api).recipes_by_meal_type("breakfast")
    assert isinstance(data.get("recipes"), list)


# -----------------------
# NEGATIVE (regression)
# -----------------------


@pytest.mark.regression
@pytest.mark.negative
def test_get_recipe_invalid_id_returns_404(api):
    r = RecipesClient(api).get_recipe_raw(0)
    assert r.status_code == 404


@pytest.mark.regression
@pytest.mark.negative
def test_recipes_by_tag_invalid_returns_error_or_empty(api):
    r = RecipesClient(api).recipes_by_tag_raw("this-tag-does-not-exist")

    if r.status_code in (404, 400):
        return

    assert r.status_code == 200
    body = r.json()
    assert "recipes" in body
    assert isinstance(body["recipes"], list)
    assert len(body["recipes"]) == 0


@pytest.mark.regression
@pytest.mark.negative
def test_search_recipes_empty_query_returns_200(api):
    r = RecipesClient(api).search_recipes_raw(q="")
    assert r.status_code == 200
    body = r.json()
    assert "recipes" in body
    assert isinstance(body["recipes"], list)
