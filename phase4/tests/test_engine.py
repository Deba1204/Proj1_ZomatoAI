"""Tests for Phase 4 / STEP 4 — Recommendation engine (no API key required for unit tests)."""

import os
from pathlib import Path

# Load phase4/.env first so GROQ_API_KEY is set before any recommendation code runs
try:
    from dotenv import load_dotenv
    # phase4/tests/test_engine.py -> phase4/.env
    _phase4_dir = Path(__file__).resolve().parent.parent
    _env_path = _phase4_dir / ".env"
    load_dotenv(dotenv_path=str(_env_path), override=True)
except Exception:
    pass

import pytest
import pandas as pd

from recommendation.engine import (
    recommend_restaurants,
    _prefilter,
    _score_and_top_candidates,
    _dataframe_to_candidates,
    _cost_column,
)
from recommendation.groq_client import (
    get_api_key,
    parse_recommendations_json,
    build_ranking_prompt,
    rank_with_groq,
)


def _sample_df():
    return pd.DataFrame({
        "city": ["btm", "btm", "btm", "church street"],
        "approx_cost(for two people)": [300, 500, 700, 500],
        "rate": [4.0, 4.5, 3.5, 4.2],
        "votes": [100, 200, 50, 150],
        "name": ["R1", "R2", "R3", "R4"],
    })


class TestCostColumn:
    def test_finds_approx_cost(self):
        df = pd.DataFrame(columns=["approx_cost(for two people)"])
        assert _cost_column(df) == "approx_cost(for two people)"

    def test_finds_alias(self):
        df = pd.DataFrame(columns=["approx_cost_for_two_people"])
        assert _cost_column(df) == "approx_cost_for_two_people"

    def test_returns_none_when_missing(self):
        df = pd.DataFrame(columns=["other"])
        assert _cost_column(df) is None


class TestPrefilter:
    def test_filters_by_city_and_cost(self):
        df = _sample_df()
        user = {"city": "btm", "min_price": 400, "max_price": 600}
        out = _prefilter(df, user)
        assert len(out) == 1
        assert out.iloc[0]["name"] == "R2"

    def test_empty_when_no_match(self):
        df = _sample_df()
        user = {"city": "unknown", "min_price": 0, "max_price": 1000}
        out = _prefilter(df, user)
        assert len(out) == 0

    def test_inclusive_bounds(self):
        df = _sample_df()
        user = {"city": "btm", "min_price": 300, "max_price": 700}
        out = _prefilter(df, user)
        assert len(out) == 3


class TestScoreAndTopCandidates:
    def test_returns_top_n_by_score(self):
        df = _sample_df().iloc[:3]
        out = _score_and_top_candidates(df, n=2)
        assert len(out) == 2
        assert "_score" in out.columns
        assert out["_score"].iloc[0] >= out["_score"].iloc[1]

    def test_empty_input_returns_empty(self):
        out = _score_and_top_candidates(pd.DataFrame(), n=10)
        assert len(out) == 0


class TestDataframeToCandidates:
    def test_returns_list_of_dicts(self):
        df = _sample_df().iloc[:2]
        cands = _dataframe_to_candidates(df)
        assert len(cands) == 2
        assert "name" in cands[0]
        assert cands[0]["name"] in ("R1", "R2")

    def test_empty_returns_empty(self):
        assert _dataframe_to_candidates(pd.DataFrame()) == []


class TestRecommendRestaurants:
    def test_returns_list_when_candidates_le_10_no_groq(self):
        """When <=10 candidates, engine returns them without calling Groq."""
        df = _sample_df().iloc[:3]
        user = {"city": "btm", "min_price": 0, "max_price": 1000}
        result = recommend_restaurants(df, user)
        assert isinstance(result, list)
        assert len(result) <= 3
        assert all("name" in r for r in result)

    def test_fallback_relax_price_retry(self):
        """When 0 rows, relax price +20% and retry once; then return up to 10 without Groq."""
        df = _sample_df()
        # No row in [600, 650]; after relax 0.8*600=480, 1.2*650=780 -> 500 and 700 match
        user = {"city": "btm", "min_price": 600, "max_price": 650}
        result = recommend_restaurants(df, user)
        assert isinstance(result, list)
        assert len(result) <= 10
        assert len(result) >= 1

    def test_empty_when_no_data_after_relax(self):
        df = pd.DataFrame({"city": ["x"], "approx_cost(for two people)": [100], "name": ["R1"], "rate": [4.0], "votes": [10]})
        user = {"city": "nonexistent", "min_price": 0, "max_price": 100}
        result = recommend_restaurants(df, user)
        assert result == []


class TestGroqClientUnit:
    def test_get_api_key_raises_when_unset(self):
        orig = os.environ.pop("GROQ_API_KEY", None)
        try:
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                get_api_key()
        finally:
            if orig is not None:
                os.environ["GROQ_API_KEY"] = orig

    def test_parse_recommendations_json(self):
        raw = '{"recommendations": [{"name": "A", "reason": "good"}, {"name": "B"}]}'
        out = parse_recommendations_json(raw)
        assert len(out) == 2
        assert out[0]["name"] == "A"
        assert out[0].get("reason") == "good"

    def test_parse_recommendations_json_in_code_block(self):
        raw = '```json\n{"recommendations": [{"name": "X"}]}\n```'
        out = parse_recommendations_json(raw)
        assert len(out) == 1
        assert out[0]["name"] == "X"

    def test_build_ranking_prompt(self):
        system, user = build_ranking_prompt([{"name": "R1"}], "btm")
        assert "btm" in user
        assert "R1" in user
        assert "top 10" in system.lower() or "recommendations" in system.lower()


class TestRecommendRestaurantsWithGroq:
    """Run only when GROQ_API_KEY is set."""

    def test_full_flow_returns_up_to_10(self):
        df = _sample_df()
        for _ in range(20):
            df = pd.concat([df, _sample_df()], ignore_index=True)
        user = {"city": "btm", "min_price": 0, "max_price": 1000}
        result = recommend_restaurants(df, user)
        assert isinstance(result, list)
        assert len(result) <= 10
        assert all(isinstance(r, dict) for r in result)


class TestLLMRecommendationIntegration:
    """Tests that the Groq LLM recommendation is actually working (real API calls)."""

    def test_llm_rank_with_groq_returns_valid_list(self):
        """Call Groq with 15 candidates; LLM must return up to 10 recommendations."""
        candidates = [
            {"name": f"Restaurant_{i}", "rate": str(4.0 + i * 0.05), "votes": str(100 + i * 10)}
            for i in range(15)
        ]
        result = rank_with_groq(candidates, city="btm")
        assert isinstance(result, list), "LLM should return a list"
        assert 1 <= len(result) <= 10, "LLM should return between 1 and 10 recommendations"
        assert all(isinstance(r, dict) for r in result), "Each item should be a dict"
        assert all("name" in r and r["name"] for r in result), "Each item must have a non-empty name"

    def test_llm_recommendations_have_expected_structure(self):
        """Returned recommendations should have name (and optionally reason)."""
        candidates = [{"name": "Place A", "rate": "4.5"}, {"name": "Place B", "rate": "4.0"}]
        result = rank_with_groq(candidates, city="test_city")
        assert len(result) >= 1
        for r in result:
            assert "name" in r, f"Recommendation missing 'name': {r}"
            assert isinstance(r["name"], str) and r["name"].strip(), f"name must be non-empty string: {r}"

    def test_llm_recommendations_are_from_candidates_only(self):
        """LLM must only choose from the candidate list (no invented restaurants)."""
        candidate_names = ["Alpha Diner", "Beta Bistro", "Gamma Grill", "Delta Cafe", "Epsilon Eats"]
        candidates = [{"name": n, "rate": "4.2", "votes": "50"} for n in candidate_names]
        result = rank_with_groq(candidates, city="downtown")
        assert len(result) >= 1
        for r in result:
            name = r.get("name", "").strip()
            # Exact match or candidate name contained in response (e.g. "Alpha Diner" in "Alpha Diner - great")
            from_list = name in candidate_names or any(c in name for c in candidate_names)
            assert from_list, (
                f"LLM returned '{name}' which is not from the candidate list {candidate_names}. "
                "LLM must only choose from the given candidates."
            )
