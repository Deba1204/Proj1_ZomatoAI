"""Tests for Phase 2 / STEP 2 — User input handler."""

import pytest
import pandas as pd

from phase2.handler import (
    UserInput,
    parse_price,
    parse_args,
    get_valid_cities_from_df,
    validate_city,
    get_validated_input,
    PRICE_BANDS,
)


class TestParsePrice:
    """Tests for parse_price."""

    def test_single_number(self):
        assert parse_price("500") == (500, 500)
        assert parse_price("0") == (0, 0)
        assert parse_price("  1200  ") == (1200, 1200)

    def test_range(self):
        assert parse_price("500-1000") == (500, 1000)
        assert parse_price("500 - 1000") == (500, 1000)
        assert parse_price("  200  -  800  ") == (200, 800)

    def test_range_invalid_order(self):
        with pytest.raises(ValueError, match="min.*cannot be greater than max"):
            parse_price("1000-500")

    def test_label_low(self):
        assert parse_price("Low") == PRICE_BANDS["low"]
        assert parse_price("low") == (0, 500)
        assert parse_price("  LOW  ") == (0, 500)

    def test_label_medium(self):
        assert parse_price("Medium") == (500, 1500)
        assert parse_price("medium") == (500, 1500)

    def test_label_high(self):
        assert parse_price("High") == (1500, 999_999)
        assert parse_price("high") == (1500, 999_999)

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_price("")
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_price("   ")

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="number.*range.*label"):
            parse_price("abc")
        with pytest.raises(ValueError, match="number.*range.*label"):
            parse_price("500-1000-2000")


class TestGetValidCitiesFromDf:
    """Tests for get_valid_cities_from_df."""

    def test_returns_lowercase_sorted(self):
        df = pd.DataFrame({"city": ["Mumbai", "bangalore", "Delhi", "mumbai"]})
        cities = get_valid_cities_from_df(df)
        assert cities == ["bangalore", "delhi", "mumbai"]

    def test_drops_nulls(self):
        df = pd.DataFrame({"city": ["a", None, "b", pd.NA]})
        cities = get_valid_cities_from_df(df)
        assert cities == ["a", "b"]

    def test_no_city_column_returns_empty(self):
        df = pd.DataFrame({"other": [1, 2]})
        assert get_valid_cities_from_df(df) == []

    def test_empty_df_returns_empty(self):
        df = pd.DataFrame(columns=["city"])
        assert get_valid_cities_from_df(df) == []


class TestValidateCity:
    """Tests for validate_city."""

    def test_case_insensitive(self):
        valid = ["bangalore", "mumbai"]
        assert validate_city("Bangalore", valid) == "bangalore"
        assert validate_city("BANGALORE", valid) == "bangalore"
        assert validate_city("bangalore", valid) == "bangalore"

    def test_returns_normalized_lowercase(self):
        valid = ["btm", "koramangala"]
        assert validate_city("BTM", valid) == "btm"

    def test_not_found_raises(self):
        valid = ["bangalore", "mumbai"]
        with pytest.raises(ValueError, match="not found"):
            validate_city("Delhi", valid)

    def test_empty_city_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_city("", ["bangalore"])
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_city("   ", ["bangalore"])


class TestParseArgs:
    """Tests for parse_args (argparse)."""

    def test_parses_city_and_price(self):
        ns = parse_args(["--city", "Bangalore", "--price", "500"])
        assert ns.city == "Bangalore"
        assert ns.price == "500"

    def test_parses_range(self):
        ns = parse_args(["--city", "Mumbai", "--price", "500-1000"])
        assert ns.city == "Mumbai"
        assert ns.price == "500-1000"

    def test_parses_label(self):
        ns = parse_args(["--city", "Delhi", "--price", "High"])
        assert ns.price == "High"

    def test_missing_city_exits(self):
        with pytest.raises(SystemExit):
            parse_args(["--price", "500"])

    def test_missing_price_exits(self):
        with pytest.raises(SystemExit):
            parse_args(["--city", "Bangalore"])


class TestGetValidatedInput:
    """Tests for get_validated_input."""

    def test_without_validation(self):
        inp = get_validated_input(
            args=["--city", "Bangalore", "--price", "500"],
            valid_cities=None,
        )
        assert inp.city == "bangalore"
        assert inp.min_price == 500
        assert inp.max_price == 500

    def test_with_validation(self):
        valid = ["bangalore", "mumbai"]
        inp = get_validated_input(
            args=["--city", "Bangalore", "--price", "500-1000"],
            valid_cities=valid,
        )
        assert inp.city == "bangalore"
        assert inp.min_price == 500
        assert inp.max_price == 1000

    def test_with_validation_invalid_city_raises(self):
        valid = ["bangalore"]
        with pytest.raises(ValueError, match="not found"):
            get_validated_input(
                args=["--city", "UnknownCity", "--price", "500"],
                valid_cities=valid,
            )

    def test_price_label_medium(self):
        inp = get_validated_input(
            args=["--city", "x", "--price", "Medium"],
            valid_cities=None,
        )
        assert inp.min_price == 500
        assert inp.max_price == 1500

    def test_user_input_repr(self):
        inp = UserInput(city="bangalore", min_price=300, max_price=700)
        assert "bangalore" in repr(inp)
        assert "300" in repr(inp)
        assert "700" in repr(inp)
