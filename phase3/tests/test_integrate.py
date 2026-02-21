"""Tests for Phase 3 / STEP 3 — Pipeline integration."""

import pytest
import pandas as pd

from pipeline.integrate import (
    run_pipeline,
    PipelineError,
    EmptyDatasetError,
    MissingColumnsError,
    _check_required_columns,
    _recommendation_engine_stub,
    _print_results_stub,
)


def _minimal_df(rows: int = 3) -> pd.DataFrame:
    """DataFrame with required columns for pipeline."""
    return pd.DataFrame({
        "city": ["btm", "btm", "church street"][:rows],
        "approx_cost(for two people)": [300, 500, 600][:rows],
        "name": ["R1", "R2", "R3"][:rows],
    })


class TestCheckRequiredColumns:
    """Tests for _check_required_columns."""

    def test_pass_with_city_and_approx_cost(self):
        df = _minimal_df()
        _check_required_columns(df)  # no raise

    def test_pass_with_approx_cost_alias(self):
        df = pd.DataFrame({
            "city": ["a"],
            "approx_cost_for_two_people": [500],
        })
        _check_required_columns(df)  # no raise

    def test_raises_when_missing_city(self):
        df = pd.DataFrame({"approx_cost(for two people)": [500]})
        with pytest.raises(MissingColumnsError, match="missing required columns"):
            _check_required_columns(df)

    def test_raises_when_missing_cost_column(self):
        df = pd.DataFrame({"city": ["a"], "other": [1]})
        with pytest.raises(MissingColumnsError, match="one of"):
            _check_required_columns(df)


class TestRecommendationEngineStub:
    """Tests for _recommendation_engine_stub."""

    def test_returns_list_of_dicts(self):
        user_input = {"city": "btm", "min_price": 500, "max_price": 1000}
        df = _minimal_df()
        results = _recommendation_engine_stub(user_input, df)
        assert isinstance(results, list)
        assert len(results) >= 1
        assert all(isinstance(r, dict) for r in results)
        assert "name" in results[0]
        assert results[0]["city"] == "btm"


class TestPrintResultsStub:
    """Tests for _print_results_stub (smoke)."""

    def test_prints_without_error(self, capsys):
        _print_results_stub([{"name": "R1"}, {"name": "R2"}])
        captured = capsys.readouterr()
        assert "Results" in captured.out
        assert "R1" in captured.out


class TestRunPipeline:
    """Tests for run_pipeline."""

    def test_success_with_injected_df_and_cli_args(self):
        df = _minimal_df()
        out = run_pipeline(df=df, cli_args=["--city", "btm", "--price", "500"])
        assert "user_input" in out
        assert out["user_input"]["city"] == "btm"
        assert out["user_input"]["min_price"] == 500
        assert out["user_input"]["max_price"] == 500
        assert "results" in out
        assert "df" in out
        assert len(out["df"]) == 3

    def test_empty_dataset_raises(self):
        df = pd.DataFrame(columns=["city", "approx_cost(for two people)"])
        with pytest.raises(EmptyDatasetError, match="empty"):
            run_pipeline(df=df, cli_args=["--city", "btm", "--price", "500"])

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"other": [1, 2, 3]})
        with pytest.raises(MissingColumnsError):
            run_pipeline(df=df, cli_args=["--city", "btm", "--price", "500"])

    def test_invalid_city_raises(self):
        df = _minimal_df()
        with pytest.raises(ValueError, match="not found|invalid"):
            run_pipeline(df=df, cli_args=["--city", "NonexistentCity", "--price", "500"])

    def test_returns_stub_results(self):
        df = _minimal_df()
        out = run_pipeline(df=df, cli_args=["--city", "btm", "--price", "Medium"])
        assert out["user_input"]["min_price"] == 500
        assert out["user_input"]["max_price"] == 1500
        assert any("[Stub]" in str(r.get("name", "")) for r in out["results"])


class TestPipelineErrors:
    """Test error hierarchy."""

    def test_empty_is_pipeline_error(self):
        assert issubclass(EmptyDatasetError, PipelineError)

    def test_missing_columns_is_pipeline_error(self):
        assert issubclass(MissingColumnsError, PipelineError)
