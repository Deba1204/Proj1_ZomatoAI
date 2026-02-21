"""
Phase 5 / STEP 5 — Full pipeline: load data → parse input → recommend → display.

Integrates all layers (STEP 1–5) and displays recommendations in CLI using rich/tabulate.
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from pipeline.integrate import run_pipeline
from pipeline.integrate import (
    PipelineError,
    EmptyDatasetError,
    MissingColumnsError,
)


def main() -> int:
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
