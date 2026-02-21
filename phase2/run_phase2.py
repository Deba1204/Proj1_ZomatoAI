"""
Run Phase 2 / STEP 2 — User Input (CLI with validation).

Loads dataset from Phase 1 to get valid cities, then parses --city and --price,
validates city, and prints UserInput (min_price, max_price).

Example CLI usage:

  # From project root (recommended)
  python -m phase2.run_phase2 --city Bangalore --price 500
  python -m phase2.run_phase2 --city Mumbai --price 500-1000
  python -m phase2.run_phase2 --city "BTM" --price Medium
  python -m phase2.run_phase2 --city bangalore --price High

  # Help
  python -m phase2.run_phase2 --help
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from phase1.loader import load_and_prepare
from input.handler import parse_user_input, parse_args_for_help


def main() -> None:
    # Parse args first so --help exits without loading dataset
    try:
        parse_args_for_help()
    except SystemExit as e:
        if e.code == 0:
            return  # --help
        raise

    print("Loading dataset for city validation...")
    df = load_and_prepare(print_schema_output=False)
    print(f"Loaded {len(df)} rows.\n")

    try:
        user_input_dict = parse_user_input(df)
        print("input/handler.py with parse_user_input(df) -> user_input_dict")
        print("Example user_input_dict:", user_input_dict)
    except ValueError as e:
        print("Validation error:", e, file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise


if __name__ == "__main__":
    main()
