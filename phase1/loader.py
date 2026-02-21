"""
Phase 1 / STEP 1 — Input the Zomato Data.

Load HuggingFace dataset, convert to DataFrame, print schema, and clean fields.
"""

import os
import re
from pathlib import Path
from typing import Optional

import pandas as pd
from datasets import load_dataset

# Cache HuggingFace datasets under project to avoid permission issues
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HF_CACHE_DIR = os.environ.get("HF_HOME", str(PROJECT_ROOT / ".cache" / "huggingface"))

# Use Naren1943 dataset (ManikaSaini/zomato-restaurant not found on Hub)
DATASET_NAME = "Naren1943/zomato-restaurant-recommendation"

# Column name variants (HuggingFace may normalize or preserve original names)
APPROX_COST_COLUMNS = ["approx_cost(for two people)", "approx_cost_for_two_people"]
RATE_COLUMN = "rate"
VOTES_COLUMN = "votes"
CITY_SOURCE_COLUMNS = ["listed_in(city)", "listed_in (city)", "location"]


def load_zomato_dataset(
    dataset_name: str = DATASET_NAME,
    split: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load Zomato dataset from HuggingFace and convert to pandas DataFrame.

    Args:
        dataset_name: HuggingFace dataset identifier.
        split: Dataset split to load (e.g. 'train', 'train[:100]'). Default: first available.

    Returns:
        Pandas DataFrame with raw dataset.
    """
    dataset = load_dataset(dataset_name, cache_dir=HF_CACHE_DIR)

    # Handle different dataset structures (DatasetDict vs Dataset)
    if hasattr(dataset, "keys"):
        split_names = list(dataset.keys())
        first_split = split or split_names[0]
        if first_split not in dataset:
            first_split = split_names[0]
        ds = dataset[first_split]
    else:
        ds = dataset

    return ds.to_pandas()


def _find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Return first matching column name from candidates, or None."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def clean_approx_cost(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert approx_cost(for two people) to numeric int.
    Handles strings like '300', '₹400', '1,000', etc.
    """
    col = _find_column(df, APPROX_COST_COLUMNS)
    if col is None:
        return df

    def _to_int(val):
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return int(val) if not pd.isna(val) else None
        s = str(val).strip()
        if not s or s.lower() in ("nan", "none", "-", ""):
            return None
        # Remove currency symbols and commas
        s = re.sub(r"[^\d.]", "", s)
        if not s:
            return None
        try:
            return int(float(s))
        except (ValueError, TypeError):
            return None

    df = df.copy()
    df[col] = df[col].apply(_to_int)
    return df


def clean_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract float rating from rate column.
    Examples: "4.1/5" -> 4.1, "4.5" -> 4.5
    Handles "NEW" and "-" as null.
    """
    if RATE_COLUMN not in df.columns:
        return df

    def _to_float(val):
        if pd.isna(val):
            return None
        s = str(val).strip()
        if not s or s.upper() == "NEW" or s == "-":
            return None
        # Extract leading float (e.g. "4.1/5" -> 4.1)
        match = re.search(r"(\d+\.?\d*)", s)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, TypeError):
                pass
        return None

    df = df.copy()
    df[RATE_COLUMN] = df[RATE_COLUMN].apply(_to_float)
    return df


def clean_votes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert votes to numeric int."""
    if VOTES_COLUMN not in df.columns:
        return df

    def _to_int(val):
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return int(val) if not pd.isna(val) else None
        s = str(val).strip()
        if not s or s == "-":
            return None
        s = re.sub(r"[^\d]", "", s)
        if not s:
            return None
        try:
            return int(s)
        except (ValueError, TypeError):
            return None

    df = df.copy()
    df[VOTES_COLUMN] = df[VOTES_COLUMN].apply(_to_int)
    return df


def clean_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create normalized city column.
    Prefer listed_in(city) over location (city-level vs area).
    Normalize to lowercase.
    """
    col = _find_column(df, CITY_SOURCE_COLUMNS)
    if col is None:
        return df

    def _normalize(val):
        if pd.isna(val):
            return None
        s = str(val).strip()
        if not s or s == "-":
            return None
        return s.lower()

    df = df.copy()
    df["city"] = df[col].apply(_normalize)
    return df


def print_schema(df: pd.DataFrame) -> None:
    """Print schema: columns and dtypes."""
    print("Schema (columns + dtypes):")
    print("-" * 60)
    for col in df.columns:
        print(f"  {col!r}: {df[col].dtype}")
    print("-" * 60)
    print(f"Total columns: {len(df.columns)}, Rows: {len(df)}")


def load_and_prepare(
    dataset_name: str = DATASET_NAME,
    split: Optional[str] = None,
    print_schema_output: bool = True,
) -> pd.DataFrame:
    """
    Load Zomato data, clean fields, and optionally print schema.

    Args:
        dataset_name: HuggingFace dataset identifier.
        split: Dataset split to load.
        print_schema_output: If True, print schema before and after cleaning.

    Returns:
        Cleaned pandas DataFrame.
    """
    df = load_zomato_dataset(dataset_name=dataset_name, split=split)

    if print_schema_output:
        print("--- Raw schema ---")
        print_schema(df)

    df = clean_approx_cost(df)
    df = clean_rate(df)
    df = clean_votes(df)
    df = clean_city(df)

    if print_schema_output:
        print("\n--- Schema after cleaning ---")
        print_schema(df)

    return df


if __name__ == "__main__":
    df = load_and_prepare()
    print("\nSample (first 3 rows, selected columns):")
    sample_cols = [c for c in ["name", "city", "rate", "votes"] if c in df.columns]
    approx_col = _find_column(df, APPROX_COST_COLUMNS)
    if approx_col:
        sample_cols.append(approx_col)
    print(df[sample_cols].head(3).to_string())
