# Phase 2 — CLI Usage

## Overview

The Phase 2 handler accepts **--city** and **--price** via argparse. City is validated against the dataset (case-insensitive). Price is converted to numeric **min_price** and **max_price**.

## Examples

```bash
# From project root (recommended)
python -m phase2.run_phase2 --city Bangalore --price 500
python -m phase2.run_phase2 --city Mumbai --price 500-1000
python -m phase2.run_phase2 --city "BTM" --price Medium
python -m phase2.run_phase2 --city bangalore --price High

# Help
python -m phase2.run_phase2 --help
```

## Price formats

| Input   | min_price | max_price |
|--------|-----------|-----------|
| `500`  | 500       | 500       |
| `500-1000` | 500   | 1000      |
| `Low`  | 0         | 500       |
| `Medium` | 500     | 1500      |
| `High` | 1500      | 999999    |

## Validation

- **City:** Must exist in the dataset (case-insensitive). The script loads the Phase 1 dataset to get valid cities.
- **Price:** Must be a number, a range (`min-max`), or a label (`Low` / `Medium` / `High`).

## Output

On success, the script prints the validated `UserInput`: `city` (normalized lowercase), `min_price`, and `max_price`.
