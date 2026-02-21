# Phase 5 — Display & full pipeline (STEP 5)

## What’s included

- **Display (STEP 5):** `display/formatter.py` — prints recommendations in a CLI table (rich or tabulate) with rank, name, rating, votes, cost_for_two, cuisines, locality, address. Handles empty results with a message suggesting increasing budget or trying a different city.
- **Integration:** Pipeline uses this display instead of the stub; `main.py` and `phase5/run_phase5.py` run the full flow (load → input → recommend → display).

## Run full pipeline (all layers)

From project root:

```bash
py main.py --city btm --price 500-1000
```

Or:

```bash
py -m phase5.run_phase5 --city btm --price 500-1000
```

## Run Phase 5 tests

```bash
py -m pytest phase5/tests -v
```
