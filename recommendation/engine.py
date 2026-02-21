"""
Recommendation engine — STEP 4.

Pre-filters by city and cost, scores candidates, calls Groq LLM to rank top 10.
"""

import math
from typing import Any, Dict, List, Optional

import pandas as pd

from recommendation.groq_client import rank_with_groq

# Column names (must match Phase 1 cleaned schema)
CITY_COL = "city"
RATE_COL = "rate"
VOTES_COL = "votes"
COST_COLUMNS = ["approx_cost(for two people)", "approx_cost_for_two_people"]
TOP_CANDIDATES = 50
TOP_RECOMMENDATIONS = 10


def _cost_column(df: pd.DataFrame) -> Optional[str]:
    for c in COST_COLUMNS:
        if c in df.columns:
            return c
    return None


def _prefilter(
    df_clean: pd.DataFrame,
    user_input: Dict[str, Any],
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
) -> pd.DataFrame:
    """Filter by city and cost_for_two between min_price and max_price (inclusive)."""
    if min_price is None:
        min_price = user_input["min_price"]
    if max_price is None:
        max_price = user_input["max_price"]

    city_val = str(user_input["city"]).strip().lower()
    cost_col = _cost_column(df_clean)
    if not cost_col:
        return pd.DataFrame()

    out = df_clean.copy()
    out = out[out[CITY_COL].astype(str).str.strip().str.lower() == city_val]
    # Drop rows where cost is NaN for filtering
    out = out[out[cost_col].notna()]
    out = out[(out[cost_col] >= min_price) & (out[cost_col] <= max_price)]
    return out


def _score_and_top_candidates(df_filtered: pd.DataFrame, n: int = TOP_CANDIDATES) -> pd.DataFrame:
    """Score = rating * log(votes + 1). Return top n by score."""
    if len(df_filtered) == 0:
        return df_filtered

    df = df_filtered.copy()
    rate = df[RATE_COL].fillna(0.0) if RATE_COL in df.columns else pd.Series(0.0, index=df.index)
    votes = df[VOTES_COL].fillna(0) if VOTES_COL in df.columns else pd.Series(0, index=df.index)
    votes = votes.astype(int)
    log_votes = (votes + 1).apply(lambda v: math.log(v))
    score = rate * log_votes
    df["_score"] = score
    df = df.sort_values("_score", ascending=False)
    return df.head(n)


def _dataframe_to_candidates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert top-candidates DataFrame to list of dicts for LLM (name, rate, votes, cost, etc.)."""
    if df is None or len(df) == 0:
        return []
    cost_col = _cost_column(df)
    cols = ["name"] if "name" in df.columns else []
    for c in [RATE_COL, VOTES_COL, "cuisines", "rest_type"]:
        if c in df.columns and c not in cols:
            cols.append(c)
    if cost_col and cost_col not in cols:
        cols.append(cost_col)
    # Ensure we have at least name
    if "name" not in df.columns and len(df.columns):
        cols = [df.columns[0]] + [c for c in cols if c != "name"]
    keep = [c for c in cols if c in df.columns]
    if not keep:
        keep = list(df.columns)[:10]
    return df[keep].fillna("").astype(str).to_dict(orient="records")


def recommend_restaurants(
    df_clean: pd.DataFrame,
    user_input: Dict[str, Any],
    top_n: int = TOP_RECOMMENDATIONS,
    groq_model: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Pre-filter by city and cost, take top 50 by score, then Groq LLM ranks to top 10.

    Fallback: if pre-filter returns 0 rows, relax price band by +20% and retry once.

    Returns:
        list[dict] with at least 'name' per item; may include 'reason' from LLM.
    """
    min_price = user_input["min_price"]
    max_price = user_input["max_price"]

    filtered = _prefilter(df_clean, user_input, min_price, max_price)
    if len(filtered) == 0:
        # Relax price by +20% and retry once
        new_min = max(0, int(min_price * 0.8))
        new_max = int(max_price * 1.2)
        filtered = _prefilter(df_clean, user_input, new_min, new_max)
        relaxed = True
    if len(filtered) == 0:
        return []

    candidates_df = _score_and_top_candidates(filtered, n=TOP_CANDIDATES)
    candidates = _dataframe_to_candidates(candidates_df)
    if len(candidates) == 0:
        return []
    # If we have <= top_n, return as-is (no need to call LLM)
    if len(candidates) <= top_n:
        return candidates[:top_n]

    result = rank_with_groq(candidates, city=user_input["city"], model=groq_model)
    return result[:top_n] if result else candidates[:top_n]


