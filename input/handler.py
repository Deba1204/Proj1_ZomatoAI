"""
Input handler — parse CLI (--city, --price) and return validated user input as dict.

Provides parse_user_input(df) -> user_input_dict.
Example user_input_dict: {"city": str, "min_price": int, "max_price": int}
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Project root for imports
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from phase2.handler import (
    get_valid_cities_from_df,
    get_validated_input,
    parse_args,
)


def parse_user_input(df) -> Dict[str, Any]:
    """
    Parse CLI arguments (--city, --price), validate against the dataset, and return
    a user input dict.

    Args:
        df: DataFrame with a "city" column (e.g. from Phase 1 loader) used for city validation.

    Returns:
        user_input_dict with keys:
          - city: str (normalized lowercase)
          - min_price: int
          - max_price: int

    Raises:
        ValueError: if city is invalid or price format is wrong.
        SystemExit: on argparse failure (e.g. missing --city/--price).
    """
    valid_cities = get_valid_cities_from_df(df)
    inp = get_validated_input(args=None, valid_cities=valid_cities)
    return {
        "city": inp.city,
        "min_price": inp.min_price,
        "max_price": inp.max_price,
    }


def parse_args_for_help() -> None:
    """Call parse_args(); used so --help works without loading df."""
    parse_args()


if __name__ == "__main__":
    # Example: requires df from Phase 1
    print("Example user_input_dict:", {"city": "btm", "min_price": 500, "max_price": 1000})
