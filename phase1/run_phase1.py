"""
Run Phase 1 / STEP 1 — Load and prepare Zomato data.

Execute from project root:
    python -m phase1.run_phase1

Or:
    cd phase1 && python run_phase1.py  (requires PYTHONPATH=.. or run from parent)
"""

import sys
from pathlib import Path

# Ensure project root is on path when run as script
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from phase1.loader import load_and_prepare

if __name__ == "__main__":
    df = load_and_prepare()
    print("\nPhase 1 complete. Loaded", len(df), "rows.")
