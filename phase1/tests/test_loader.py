"""Tests for Phase 1 / STEP 1 — Zomato data loader."""

import pytest
import pandas as pd

from phase1.loader import (
    clean_approx_cost,
    clean_rate,
    clean_votes,
    clean_city,
    load_zomato_dataset,
    load_and_prepare,
    print_schema,
    _find_column,
    APPROX_COST_COLUMNS,
    CITY_SOURCE_COLUMNS,
    DATASET_NAME,
)


# --- Unit tests for cleaning functions ---


class TestCleanApproxCost:
    """Tests for clean_approx_cost."""

    def test_string_numbers(self):
        df = pd.DataFrame({"approx_cost(for two people)": ["300", "500", "1000"]})
        result = clean_approx_cost(df)
        assert list(result["approx_cost(for two people)"]) == [300, 500, 1000]

    def test_currency_symbol(self):
        df = pd.DataFrame({"approx_cost(for two people)": ["₹400", "₹1,200"]})
        result = clean_approx_cost(df)
        assert list(result["approx_cost(for two people)"]) == [400, 1200]

    def test_comma_separated(self):
        df = pd.DataFrame({"approx_cost(for two people)": ["1,000", "2,500"]})
        result = clean_approx_cost(df)
        assert list(result["approx_cost(for two people)"]) == [1000, 2500]

    def test_null_and_invalid(self):
        df = pd.DataFrame({
            "approx_cost(for two people)": ["300", None, "", "-", "nan", 400]
        })
        result = clean_approx_cost(df)
        assert result["approx_cost(for two people)"].iloc[0] == 300
        assert pd.isna(result["approx_cost(for two people)"].iloc[1])
        assert pd.isna(result["approx_cost(for two people)"].iloc[2])
        assert pd.isna(result["approx_cost(for two people)"].iloc[3])
        assert pd.isna(result["approx_cost(for two people)"].iloc[4])
        assert result["approx_cost(for two people)"].iloc[5] == 400

    def test_alternative_column_name(self):
        df = pd.DataFrame({"approx_cost_for_two_people": ["300", "500"]})
        result = clean_approx_cost(df)
        assert list(result["approx_cost_for_two_people"]) == [300, 500]

    def test_missing_column_unchanged(self):
        df = pd.DataFrame({"other": [1, 2, 3]})
        result = clean_approx_cost(df)
        assert "other" in result.columns
        pd.testing.assert_frame_equal(result, df)


class TestCleanRate:
    """Tests for clean_rate."""

    def test_fraction_format(self):
        df = pd.DataFrame({"rate": ["4.1/5", "4.5/5", "3.8/5"]})
        result = clean_rate(df)
        assert list(result["rate"]) == [4.1, 4.5, 3.8]

    def test_new_as_null(self):
        df = pd.DataFrame({"rate": ["NEW", "4.2/5", "new"]})
        result = clean_rate(df)
        assert pd.isna(result["rate"].iloc[0])
        assert result["rate"].iloc[1] == 4.2
        assert pd.isna(result["rate"].iloc[2])

    def test_dash_as_null(self):
        df = pd.DataFrame({"rate": ["-", "4.0/5"]})
        result = clean_rate(df)
        assert pd.isna(result["rate"].iloc[0])
        assert result["rate"].iloc[1] == 4.0

    def test_plain_number(self):
        df = pd.DataFrame({"rate": ["4.5", "3.2"]})
        result = clean_rate(df)
        assert list(result["rate"]) == [4.5, 3.2]

    def test_missing_column_unchanged(self):
        df = pd.DataFrame({"other": [1, 2]})
        result = clean_rate(df)
        pd.testing.assert_frame_equal(result, df)


class TestCleanVotes:
    """Tests for clean_votes."""

    def test_numeric_strings(self):
        df = pd.DataFrame({"votes": ["100", "500", "1200"]})
        result = clean_votes(df)
        assert list(result["votes"]) == [100, 500, 1200]

    def test_already_int(self):
        df = pd.DataFrame({"votes": [100, 500, 0]})
        result = clean_votes(df)
        assert list(result["votes"]) == [100, 500, 0]

    def test_null_and_dash(self):
        df = pd.DataFrame({"votes": ["100", None, "-", ""]})
        result = clean_votes(df)
        assert result["votes"].iloc[0] == 100
        assert pd.isna(result["votes"].iloc[1])
        assert pd.isna(result["votes"].iloc[2])
        assert pd.isna(result["votes"].iloc[3])

    def test_missing_column_unchanged(self):
        df = pd.DataFrame({"other": [1, 2]})
        result = clean_votes(df)
        pd.testing.assert_frame_equal(result, df)


class TestCleanCity:
    """Tests for clean_city."""

    def test_prefers_listed_in_city(self):
        df = pd.DataFrame({
            "listed_in(city)": ["Bangalore", "Mumbai"],
            "location": ["BTM", "Bandra"],
        })
        result = clean_city(df)
        assert "city" in result.columns
        assert list(result["city"]) == ["bangalore", "mumbai"]

    def test_uses_location_when_listed_in_city_missing(self):
        df = pd.DataFrame({
            "location": ["BTM", "Koramangala"],
        })
        result = clean_city(df)
        assert list(result["city"]) == ["btm", "koramangala"]

    def test_normalize_lowercase(self):
        df = pd.DataFrame({"listed_in(city)": ["BANGALORE", "Mumbai"]})
        result = clean_city(df)
        assert list(result["city"]) == ["bangalore", "mumbai"]

    def test_null_and_dash(self):
        df = pd.DataFrame({"listed_in(city)": ["Bangalore", None, "-", ""]})
        result = clean_city(df)
        assert result["city"].iloc[0] == "bangalore"
        assert pd.isna(result["city"].iloc[1])
        assert pd.isna(result["city"].iloc[2])
        assert pd.isna(result["city"].iloc[3])

    def test_missing_column_unchanged(self):
        df = pd.DataFrame({"other": ["a", "b"]})
        result = clean_city(df)
        assert "city" not in result.columns
        pd.testing.assert_frame_equal(result, df)


class TestFindColumn:
    """Tests for _find_column helper."""

    def test_finds_first_match(self):
        df = pd.DataFrame(columns=["a", "approx_cost(for two people)", "b"])
        col = _find_column(df, APPROX_COST_COLUMNS)
        assert col == "approx_cost(for two people)"

    def test_finds_alternative(self):
        df = pd.DataFrame(columns=["other", "approx_cost_for_two_people"])
        col = _find_column(df, APPROX_COST_COLUMNS)
        assert col == "approx_cost_for_two_people"

    def test_returns_none_when_missing(self):
        df = pd.DataFrame(columns=["x", "y"])
        col = _find_column(df, APPROX_COST_COLUMNS)
        assert col is None


class TestPrintSchema:
    """Tests for print_schema (smoke test)."""

    def test_prints_without_error(self, capsys):
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        print_schema(df)
        captured = capsys.readouterr()
        assert "a" in captured.out
        assert "b" in captured.out
        assert "int64" in captured.out or "object" in captured.out


class TestLoadAndPrepare:
    """Integration tests — require network for load_dataset."""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires network access to HuggingFace")
    def test_load_and_prepare_returns_dataframe(self):
        df = load_and_prepare(print_schema_output=False)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires network access to HuggingFace")
    def test_load_and_prepare_has_cleaned_columns(self):
        df = load_and_prepare(print_schema_output=False)
        # At least one of the expected columns should exist
        all_cols = set(df.columns)
        has_city = "city" in all_cols or any(c in all_cols for c in CITY_SOURCE_COLUMNS)
        has_cost = any(c in all_cols for c in APPROX_COST_COLUMNS)
        assert has_city or has_cost or "rate" in all_cols or "votes" in all_cols


# --- Smoke test: run cleaning pipeline on mock data ---


def test_full_cleaning_pipeline_on_mock_data():
    """Test full cleaning pipeline on mock data (no network)."""
    raw = pd.DataFrame({
        "name": ["R1", "R2", "R3"],
        "approx_cost(for two people)": ["₹300", "500", "1,000"],
        "rate": ["4.1/5", "NEW", "-"],
        "votes": ["100", "50", "-"],
        "listed_in(city)": ["Bangalore", "Mumbai", "Delhi"],
    })
    df = clean_approx_cost(raw)
    df = clean_rate(df)
    df = clean_votes(df)
    df = clean_city(df)

    assert list(df["approx_cost(for two people)"]) == [300, 500, 1000]
    assert df["rate"].iloc[0] == 4.1
    assert pd.isna(df["rate"].iloc[1])
    assert pd.isna(df["rate"].iloc[2])
    assert df["votes"].iloc[0] == 100 and df["votes"].iloc[1] == 50
    assert pd.isna(df["votes"].iloc[2])
    assert list(df["city"]) == ["bangalore", "mumbai", "delhi"]
