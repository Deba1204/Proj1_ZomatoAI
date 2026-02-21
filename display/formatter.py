"""
STEP 5 — Display recommendations in CLI using rich or tabulate.

Shows: rank, name, rating, votes, cost_for_two, cuisines, locality, address.
Handles empty result set with a friendly message.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

# Optional rich; fallback to tabulate
try:
    from rich.console import Console
    from rich.table import Table
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

try:
    from tabulate import tabulate
    _TABULATE_AVAILABLE = True
except ImportError:
    _TABULATE_AVAILABLE = False

COST_COLUMNS = ["approx_cost(for two people)", "approx_cost_for_two_people"]
MAX_CUISINES = 40
MAX_ADDRESS = 50


def _cost_col(df: pd.DataFrame) -> Optional[str]:
    for c in COST_COLUMNS:
        if c in df.columns:
            return c
    return None


def _enrich_from_df(
    result: Dict[str, Any],
    df: pd.DataFrame,
    city: Optional[str] = None,
) -> Dict[str, Any]:
    """Look up a row in df by name (and optionally city) to get rating, votes, cost, cuisines, address."""
    name = (result.get("name") or "").strip()
    if not name:
        return result
    mask = df["name"].astype(str).str.strip() == name
    if city:
        mask = mask & (df["city"].astype(str).str.strip().str.lower() == city.lower())
    match = df.loc[mask]
    if len(match) == 0:
        return result
    row = match.iloc[0]
    out = dict(result)
    if "rate" in df.columns and pd.notna(row.get("rate")):
        out["rating"] = row["rate"]
    if "votes" in df.columns and pd.notna(row.get("votes")):
        out["votes"] = row["votes"]
    cost_col = _cost_col(df)
    if cost_col and pd.notna(row.get(cost_col)):
        out["cost_for_two"] = row[cost_col]
    if "cuisines" in df.columns and pd.notna(row.get("cuisines")):
        c = str(row["cuisines"]).strip()
        out["cuisines"] = c[:MAX_CUISINES] + "..." if len(c) > MAX_CUISINES else c
    if "location" in df.columns and pd.notna(row.get("location")):
        out["locality"] = str(row["location"]).strip()
    elif "city" in df.columns and pd.notna(row.get("city")):
        out["locality"] = str(row["city"]).strip()
    if "address" in df.columns and pd.notna(row.get("address")):
        a = str(row["address"]).strip()
        out["address"] = a[:MAX_ADDRESS] + "..." if len(a) > MAX_ADDRESS else a
    return out


def enrich_recommendations_for_api(
    results: List[Dict[str, Any]],
    df: pd.DataFrame,
    city: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Enrich raw recommendation list from dataframe for API/JSON (e.g. React frontend)."""
    if not results or df is None or len(df) == 0:
        return results
    return [_enrich_from_df(r, df, city=city) for r in results]


def _row_to_list(rank: int, r: Dict[str, Any]) -> List[str]:
    """Build a row for table: rank, name, rating, votes, cost_for_two, cuisines, locality, address."""
    return [
        str(rank),
        str(r.get("name", "")).strip() or "—",
        str(r.get("rating", r.get("rate", ""))).strip() or "—",
        str(r.get("votes", "")).strip() or "—",
        str(r.get("cost_for_two", "")).strip() or "—",
        str(r.get("cuisines", "")).strip() or "—",
        str(r.get("locality", "")).strip() or "—",
        str(r.get("address", "")).strip() or "—",
    ]


def display_recommendations(
    results: List[Dict[str, Any]],
    df: Optional[pd.DataFrame] = None,
    user_input: Optional[Dict[str, Any]] = None,
    use_rich: bool = True,
) -> None:
    """
    Print recommendations as a clean numbered table (rich or tabulate).
    If results are empty, print a friendly message suggesting increasing budget or different city.
    """
    city = (user_input or {}).get("city", "")
    if not results:
        _print_empty_message(city)
        return
    # Enrich from dataframe if available
    if df is not None and len(df) > 0:
        enriched = [_enrich_from_df(r, df, city=city) for r in results]
    else:
        enriched = results
    headers = ["Rank", "Name", "Rating", "Votes", "Cost (for 2)", "Cuisines", "Locality", "Address"]
    rows = [_row_to_list(i, r) for i, r in enumerate(enriched, 1)]
    if use_rich and _RICH_AVAILABLE:
        _print_rich_table(headers, rows)
    elif _TABULATE_AVAILABLE:
        _print_tabulate(headers, rows)
    else:
        _print_plain(headers, rows)


def _print_empty_message(city: str) -> None:
    msg = (
        "No recommendations found for your criteria.\n\n"
        "  • Try increasing your budget (e.g. use a higher price range or \"Medium\" / \"High\").\n"
        "  • Try a different city or locality."
    )
    if city:
        msg = f"No recommendations found for '{city}'.\n\n" + msg.split("\n\n", 1)[1]
    if _RICH_AVAILABLE:
        from rich.console import Console
        from rich.panel import Panel
        Console().print(Panel(msg, title="[bold yellow]No results[/bold yellow]", border_style="yellow"))
    else:
        print("No results")
        print(msg)


def _print_rich_table(headers: List[str], rows: List[List[str]]) -> None:
    table = Table(show_header=True, header_style="bold", title="Restaurant recommendations")
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*row)
    Console().print(table)


def _print_tabulate(headers: List[str], rows: List[List[str]]) -> None:
    print(tabulate(rows, headers=headers, tablefmt="simple", showindex=False))


def _print_plain(headers: List[str], rows: List[List[str]]) -> None:
    print("Restaurant recommendations")
    print("  " + " | ".join(headers))
    for row in rows:
        print("  " + " | ".join(row))
