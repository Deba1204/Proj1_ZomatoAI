"""
Zomato AI Restaurant Recommendation — main entry point.

Calls run_pipeline() (STEP 3): load data → parse input → recommend (stub) → print (stub).
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from pipeline.integrate import (
    run_pipeline,
    PipelineError,
    EmptyDatasetError,
    MissingColumnsError,
)


def main() -> int:
    # --help is handled by parse_user_input path (argparse) after load; exit early if only -h/--help
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help")):
        from input.handler import parse_args_for_help
        try:
            parse_args_for_help()
        except SystemExit as e:
            return 0 if e.code == 0 else (e.code or 1)
        return 0

    try:
        run_pipeline()
        return 0
    except EmptyDatasetError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except MissingColumnsError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except PipelineError as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except SystemExit as e:
        return 0 if e.code == 0 else (e.code or 1)


if __name__ == "__main__":
    sys.exit(main())
