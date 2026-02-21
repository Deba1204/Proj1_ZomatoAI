"""Integration tests for Phase 5 — full pipeline and display (STEP 5)."""

import pytest
import pandas as pd

from display.formatter import display_recommendations
from pipeline.integrate import run_pipeline


def _sample_df():
    return pd.DataFrame({
        "name": ["Cafe A", "Cafe B", "Cafe C"],
        "city": ["btm", "btm", "btm"],
        "rate": [4.2, 4.5, 3.8],
        "votes": [100, 200, 50],
        "approx_cost(for two people)": [400, 600, 300],
        "cuisines": ["North Indian", "South Indian", "Chinese"],
        "location": ["BTM 1st Stage", "BTM 2nd Stage", "BTM Layout"],
        "address": ["123 Main St", "456 Park Rd", "789 Lake Ave"],
    })


class TestDisplayRecommendations:
    """Integration tests for display layer."""

    def test_display_shows_table_with_expected_columns(self, capsys):
        """Display with non-empty results prints a table with rank, name, rating, votes, cost, cuisines, locality, address."""
        results = [{"name": "Cafe A"}, {"name": "Cafe B"}]
        df = _sample_df()
        user_input = {"city": "btm", "min_price": 0, "max_price": 1000}
        display_recommendations(results, df=df, user_input=user_input, use_rich=False)
        out = capsys.readouterr().out
        # Tabulate or plain prints headers and rows
        assert "Name" in out or "name" in out.lower()
        assert "Rating" in out or "rating" in out.lower()
        assert "Votes" in out or "votes" in out.lower()
        assert "Cost" in out or "cost" in out.lower()
        assert "Cuisines" in out or "cuisines" in out.lower()
        assert "Locality" in out or "locality" in out.lower()
        assert "Address" in out or "address" in out.lower()
        assert "Cafe A" in out
        assert "Cafe B" in out

    def test_display_empty_shows_friendly_message(self, capsys):
        """Empty results print a message suggesting increasing budget or different city."""
        display_recommendations([], df=None, user_input={"city": "btm"}, use_rich=False)
        out = capsys.readouterr().out
        assert "No results" in out or "recommendations" in out.lower()
        assert "budget" in out.lower() or "price" in out.lower() or "Medium" in out or "High" in out
        assert "city" in out.lower() or "locality" in out.lower()

    def test_display_enriches_from_df(self, capsys):
        """Display enriches results with rating, votes, cost, cuisines, locality, address from df."""
        results = [{"name": "Cafe A"}]
        df = _sample_df()
        display_recommendations(results, df=df, user_input={"city": "btm"}, use_rich=False)
        out = capsys.readouterr().out
        assert "4.2" in out or "4" in out
        assert "100" in out
        assert "400" in out
        assert "North Indian" in out
        assert "BTM" in out or "Main" in out


class TestFullPipelineIntegration:
    """Integration tests for full pipeline (all layers)."""

    def test_run_pipeline_with_injected_data_returns_and_displays(self, capsys):
        """Full pipeline with injected df and cli_args runs and display produces output."""
        df = _sample_df()
        out = run_pipeline(df=df, cli_args=["--city", "btm", "--price", "500-700"])
        assert "user_input" in out
        assert out["user_input"]["city"] == "btm"
        assert "results" in out
        assert "df" in out
        captured = capsys.readouterr().out
        # Display should have run (table or at least "recommendations")
        assert "recommendations" in captured.lower() or "Name" in captured or "Rank" in captured

    def test_run_pipeline_empty_result_shows_friendly_message(self, capsys):
        """When no restaurants match, pipeline displays friendly empty message."""
        df = _sample_df()
        # City that doesn't exist in df
        out = run_pipeline(df=df, cli_args=["--city", "btm", "--price", "99999-99999"])
        assert out["results"] == []
        captured = capsys.readouterr().out
        assert "budget" in captured.lower() or "city" in captured.lower() or "No results" in captured
