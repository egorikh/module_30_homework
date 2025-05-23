import pytest
from database import Base
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_db():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(test_db):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


TEST_RECIPE = {
    "recipe_name": "Тестовый рецепт",
    "time_to_cook_in_min": 30,
    "ingredients": "тест1, тест2",
    "description": "Тестовое описание",
}


class TestRecipesAPI:
    def test_create_recipe_with_200_status_code(self, test_client):
        response = test_client.post("/recipes", json=TEST_RECIPE)
        assert response.status_code == 200

    def test_create_recipe_with_correct_recipe_name(self, test_client):
        response = test_client.post("/recipes", json=TEST_RECIPE)
        data = response.json()
        assert data["recipe_name"] == TEST_RECIPE["recipe_name"]

    def test_create_recipe_with_correct_id(self, test_client):
        response = test_client.post("/recipes", json=TEST_RECIPE)
        data = response.json()
        assert "id" in data

    def test_get_recipes_list_with_200_status_code(self, test_client):
        test_client.post("/recipes", json=TEST_RECIPE)
        response = test_client.get("/recipes")
        assert response.status_code == 200

    def test_get_recipes_list_with_correct_recipe_name(self, test_client):
        test_client.post("/recipes", json=TEST_RECIPE)
        response = test_client.get("/recipes")
        data = response.json()
        assert data[0]["recipe_name"] == TEST_RECIPE["recipe_name"]

    def test_get_recipe_detail_with_200_status_code(self, test_client):
        create_response = test_client.post("/recipes", json=TEST_RECIPE)
        recipe_id = create_response.json()["id"]
        response = test_client.get(f"/recipes/{recipe_id}")
        assert response.status_code == 200

    def test_get_recipe_detail_with_correct_id(self, test_client):
        create_response = test_client.post("/recipes", json=TEST_RECIPE)
        recipe_id = create_response.json()["id"]
        response = test_client.get(f"/recipes/{recipe_id}")
        data = response.json()
        assert data["id"] == recipe_id

    def test_get_recipe_detail_with_increasing_views(self, test_client):
        create_response = test_client.post("/recipes", json=TEST_RECIPE)
        recipe_id = create_response.json()["id"]
        response = test_client.get(f"/recipes/{recipe_id}")
        data = response.json()
        assert data["views"] == 1

    def test_invalid_recipe_creation(self, test_client):
        invalid_data = {
            "recipe_name": "",
            "time_to_cook_in_min": -5,
            "ingredients": "",
            "description": "",
        }
        response = test_client.post("/recipes", json=invalid_data)
        assert response.status_code == 422

    def test_nonexistent_recipe(self, test_client):
        response = test_client.get("/recipes/9999")
        assert response.status_code == 404
