"""
Pipeline / STEP 3 — Integrate data load, user input, recommendation (stub), and display (stub).

Provides run_pipeline() with graceful error handling:
- invalid city
- empty dataset
- missing columns
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Required columns for pipeline (city + at least one price column)
REQUIRED_COLUMNS = ["city"]
APPROX_COST_ALIASES = ["approx_cost(for two people)", "approx_cost_for_two_people"]


class PipelineError(Exception):
    """Base for pipeline errors with user-friendly messages."""

    pass


class EmptyDatasetError(PipelineError):
    """Raised when the loaded dataset has no rows."""

    pass


class MissingColumnsError(PipelineError):
    """Raised when required columns are missing from the dataset."""

    pass


def _ensure_project_path() -> None:
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))


def _load_cleaned_dataset(print_schema: bool = False) -> pd.DataFrame:
    """Load cleaned dataset from STEP 1 (Phase 1)."""
    from phase1.loader import load_and_prepare
    return load_and_prepare(print_schema_output=print_schema)


def _parse_user_input(df: pd.DataFrame) -> Dict[str, Any]:
    """Parse user input from STEP 2 (input.handler)."""
    from input.handler import parse_user_input
    return parse_user_input(df)


def _check_required_columns(df: pd.DataFrame) -> None:
    """Ensure required columns exist. Raises MissingColumnsError if not."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise MissingColumnsError(
            f"Dataset is missing required columns: {missing}. "
            f"Available: {list(df.columns)}"
        )
    has_cost = any(c in df.columns for c in APPROX_COST_ALIASES)
    if not has_cost:
        raise MissingColumnsError(
            f"Dataset must have one of {APPROX_COST_ALIASES}. "
            f"Available: {list(df.columns)}"
        )


def _run_recommendation_engine(
    user_input_dict: Dict[str, Any],
    df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """STEP 4: Run recommendation engine (Groq LLM). Requires GROQ_API_KEY."""
    from recommendation.engine import recommend_restaurants
    return recommend_restaurants(df, user_input_dict)


def _display_results(
    results: List[Dict[str, Any]],
    df: pd.DataFrame,
    user_input_dict: Dict[str, Any],
) -> None:
    """STEP 5: Display recommendations (rich/tabulate table) or friendly empty message."""
    from display.formatter import display_recommendations
    display_recommendations(results, df=df, user_input=user_input_dict)


def run_pipeline(
    print_schema: bool = False,
    df: Optional[pd.DataFrame] = None,
    cli_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Run the full pipeline: load data → parse input → recommend (STEP 4 Groq LLM) → print (stub).

    Args:
        print_schema: If True, Phase 1 prints schema.
        df: Optional pre-loaded DataFrame (skips STEP 1 load when provided).
        cli_args: Optional CLI args for input parsing (e.g. ["--city", "btm", "--price", "500"]).
                  When None, uses sys.argv (normal CLI).

    Returns:
        Dict with keys: "user_input", "results", "df" (loaded or passed-in).
        On error, raises PipelineError, ValueError (invalid city), or SystemExit (argparse).

    Raises:
        EmptyDatasetError: Dataset has no rows.
        MissingColumnsError: Required columns (e.g. city, approx cost) missing.
        ValueError: Invalid city or price (from STEP 2).
    """
    _ensure_project_path()

    # STEP 1: Load cleaned dataset
    if df is None:
        df = _load_cleaned_dataset(print_schema=print_schema)
    else:
        df = pd.DataFrame(df) if not isinstance(df, pd.DataFrame) else df

    if len(df) == 0:
        raise EmptyDatasetError("Dataset is empty. Cannot run pipeline.")

    _check_required_columns(df)

    # STEP 2: Parse user input (may raise ValueError for invalid city/price)
    if cli_args is not None:
        from phase2.handler import get_valid_cities_from_df, get_validated_input
        valid_cities = get_valid_cities_from_df(df)
        inp = get_validated_input(args=cli_args, valid_cities=valid_cities)
        user_input_dict = {"city": inp.city, "min_price": inp.min_price, "max_price": inp.max_price}
    else:
        user_input_dict = _parse_user_input(df)

    # STEP 3 → 4: Recommendation (Groq LLM; requires GROQ_API_KEY)
    results = _run_recommendation_engine(user_input_dict, df)

    # STEP 5: Display results (rich/tabulate; empty → friendly message)
    _display_results(results, df, user_input_dict)

    return {
        "user_input": user_input_dict,
        "results": results,
        "df": df,
    }


if __name__ == "__main__":
    try:
        run_pipeline()
    except PipelineError as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)
