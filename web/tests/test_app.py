"""Unit tests for STEP 6 FastAPI backend: /api/cities and /api/recommend."""

import pytest
from unittest.mock import patch


class TestApiCities:
    """GET /api/cities — returns list of valid cities from dataset."""

    def test_returns_200_and_cities_list(self, client):
        response = client.get("/api/cities")
        assert response.status_code == 200
        data = response.json()
        assert "cities" in data
        assert isinstance(data["cities"], list)
        assert "btm" in data["cities"]

    def test_cities_sorted_and_lowercase(self, client):
        response = client.get("/api/cities")
        assert response.status_code == 200
        cities = response.json()["cities"]
        assert cities == sorted(cities)
        assert all(c == c.lower() for c in cities)


class TestApiRecommendValidation:
    """POST /api/recommend — validation errors return 400 with ok: false and error message."""

    def test_invalid_city_returns_400(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "nonexistent_city_xyz", "price": "500"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("ok") is False
        assert "error" in data
        assert "not found" in data["error"].lower() or "invalid" in data["error"].lower()

    def test_empty_city_returns_400(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "   ", "price": "500"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("ok") is False
        assert "error" in data

    def test_invalid_price_returns_400(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "not-a-number"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("ok") is False
        assert "error" in data
        assert "price" in data["error"].lower() or "number" in data["error"].lower()

    def test_invalid_price_range_returns_400(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "1000-500"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data.get("ok") is False
        assert "error" in data


class TestApiRecommendSuccess:
    """POST /api/recommend — valid request returns 200 and API contract shape (mock LLM)."""

    @pytest.fixture(autouse=True)
    def mock_recommend_engine(self):
        """Avoid calling Groq; return fixed list so we assert response shape."""
        with patch("recommendation.engine.recommend_restaurants") as m:
            m.return_value = [
                {"name": "Cafe A", "rating": 4.2, "votes": 100},
                {"name": "Restaurant B", "rating": 4.0, "votes": 50},
            ]
            yield m

    def test_valid_request_returns_200(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "500"},
        )
        assert response.status_code == 200

    def test_response_has_contract_shape(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "500-1000"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True
        assert "user_input" in data
        assert data["user_input"]["city"] == "btm"
        assert data["user_input"]["min_price"] == 500
        assert data["user_input"]["max_price"] == 1000
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert data.get("empty") is False

    def test_recommendations_have_expected_fields(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "Medium"},
        )
        assert response.status_code == 200
        data = response.json()
        recs = data["recommendations"]
        assert len(recs) >= 1
        first = recs[0]
        for key in ("name", "rating", "votes", "cost_for_two", "cuisines", "locality", "address"):
            assert key in first

    def test_price_label_medium_parsed(self, client):
        response = client.post(
            "/api/recommend",
            json={"city": "btm", "price": "Medium"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_input"]["min_price"] == 500
        assert data["user_input"]["max_price"] == 1500

    def test_empty_recommendations_returns_200_with_empty_true_and_message(self, client):
        """When engine returns no results, API returns 200, empty=True, and a message."""
        with patch("recommendation.engine.recommend_restaurants") as m:
            m.return_value = []
            response = client.post(
                "/api/recommend",
                json={"city": "btm", "price": "50000"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True
        assert data.get("empty") is True
        assert data.get("recommendations") == []
        assert "message" in data
        assert data["message"]
