"""
Phase 2 / STEP 2 — User Input.

CLI input handler using argparse: --city and --price.
Validates city against dataset (case-insensitive) and converts price to min_price/max_price.
"""

import argparse
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pandas as pd

# Price bands (Low / Medium / High) as (min, max) inclusive
PRICE_BANDS = {
    "low": (0, 500),
    "medium": (500, 1500),
    "high": (1500, 999_999),
}


@dataclass
class UserInput:
    """Validated user input: city and price range."""

    city: str
    min_price: int
    max_price: int

    def __repr__(self) -> str:
        return f"UserInput(city={self.city!r}, min_price={self.min_price}, max_price={self.max_price})"


def parse_price(price_str: str) -> Tuple[int, int]:
    """
    Convert price input to (min_price, max_price).

    Accepts:
      - Single number: e.g. "500" -> (500, 500)
      - Range: e.g. "500-1000" or "500-1000" -> (500, 1000)
      - Label: "Low", "Medium", "High" (case-insensitive) -> corresponding band

    Returns:
        (min_price, max_price) as integers.

    Raises:
        ValueError: if format is invalid.
    """
    if not price_str or not str(price_str).strip():
        raise ValueError("Price cannot be empty")

    s = str(price_str).strip()

    # Label: Low / Medium / High
    label = s.lower()
    if label in PRICE_BANDS:
        return PRICE_BANDS[label]

    # Range: 500-1000 (allow spaces around hyphen)
    range_match = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", s, re.IGNORECASE)
    if range_match:
        low, high = int(range_match.group(1)), int(range_match.group(2))
        if low > high:
            raise ValueError(f"Invalid range: min ({low}) cannot be greater than max ({high})")
        return (low, high)

    # Single number
    single_match = re.match(r"^\s*(\d+)\s*$", s)
    if single_match:
        val = int(single_match.group(1))
        return (val, val)

    raise ValueError(
        f"Price must be a number (e.g. 500), a range (e.g. 500-1000), or a label (Low/Medium/High). Got: {s!r}"
    )


def get_valid_cities_from_df(df: pd.DataFrame) -> List[str]:
    """Return sorted list of unique non-null city values from DataFrame (lowercase)."""
    if "city" not in df.columns:
        return []
    cities = df["city"].dropna().astype(str).str.strip()
    cities = cities[cities.str.len() > 0]
    return sorted(cities.str.lower().unique().tolist())


def validate_city(city: str, valid_cities: List[str]) -> str:
    """
    Validate that city exists in valid_cities (case-insensitive).
    Returns the normalized city (lowercase) as it appears in the dataset.

    Raises:
        ValueError: if city is not in valid_cities.
    """
    if not city or not str(city).strip():
        raise ValueError("City cannot be empty")

    city_clean = str(city).strip().lower()
    valid_lower = {c.lower(): c for c in valid_cities}
    # Return the canonical form (lowercase) for consistency with phase1 loader
    if city_clean in valid_lower:
        return city_clean
    raise ValueError(
        f"City {city!r} not found in dataset. Valid cities (sample): {sorted(valid_cities)[:10]}..."
    )


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Build argparse parser for --city and --price. Parse and return namespace.

    Args:
        args: Command-line args (default: sys.argv[1:]).

    Returns:
        Namespace with city, price, and optionally min_price, max_price if parse_price ran.
    """
    parser = argparse.ArgumentParser(
        description="Zomato Restaurant Recommendation — provide city and price (e.g. 500, 500-1000, or Low/Medium/High)."
    )
    parser.add_argument(
        "--city",
        type=str,
        required=True,
        help="City name (must exist in dataset; case-insensitive)",
    )
    parser.add_argument(
        "--price",
        type=str,
        required=True,
        help="Budget: single number (500), range (500-1000), or label (Low/Medium/High)",
    )
    return parser.parse_args(args)


def get_validated_input(
    args: Optional[List[str]] = None,
    valid_cities: Optional[List[str]] = None,
) -> UserInput:
    """
    Parse CLI args, validate city, convert price to min/max; return UserInput.

    Args:
        args: Command-line args (default: sys.argv[1:]).
        valid_cities: List of valid city names (e.g. from dataset). If None, city is not validated.

    Returns:
        UserInput with city (normalized lowercase), min_price, max_price.

    Raises:
        ValueError: on validation failure.
    """
    ns = parse_args(args)
    min_price, max_price = parse_price(ns.price)
    city_raw = (ns.city or "").strip()
    if not city_raw:
        raise ValueError("City cannot be empty")

    if valid_cities is not None:
        city = validate_city(ns.city, valid_cities)
    else:
        city = city_raw.lower()

    return UserInput(city=city, min_price=min_price, max_price=max_price)


if __name__ == "__main__":
    # Standalone: no validation (valid_cities=None)
    try:
        inp = get_validated_input(valid_cities=None)
        print("Parsed (no city validation):", inp)
    except (ValueError, SystemExit) as e:
        print("Error:", e)
