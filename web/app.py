"""
STEP 6 — FastAPI backend for React frontend.

Endpoints:
  GET  /api/cities     — list of valid city/locality values
  POST /api/recommend  — body: { city, price }; returns recommendations or error
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# In-memory cache for dataset (loaded on first use)
_cached_df: Any = None


def get_df():
    """Load and cache dataset; used as FastAPI dependency for testability."""
    global _cached_df
    if _cached_df is None:
        from phase1.loader import load_and_prepare
        _cached_df = load_and_prepare(print_schema_output=False)
    return _cached_df


app = FastAPI(title="Zomato Recommendation API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    city: str
    price: str  # e.g. "500", "500-1000", "Low", "Medium", "High"


class RecommendResponse(BaseModel):
    ok: bool
    user_input: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    empty: Optional[bool] = None
    message: Optional[str] = None
    error: Optional[str] = None


def _to_serializable(obj: Any) -> Any:
    """Convert numpy/pandas scalars to native Python for JSON response."""
    if hasattr(obj, "item"):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_serializable(v) for v in obj]
    return obj


@app.get("/api/cities")
def api_cities(df: Any = Depends(get_df)) -> Dict[str, List[str]]:
    """Return list of valid city/locality values for dropdown."""
    try:
        from phase2.handler import get_valid_cities_from_df
        cities = get_valid_cities_from_df(df)
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend")
def api_recommend(req: RecommendRequest, df: Any = Depends(get_df)):
    """Run pipeline for given city and price; return recommendations or error."""
    try:
        from phase2.handler import get_valid_cities_from_df, get_validated_input
        from recommendation.engine import recommend_restaurants
        from display.formatter import enrich_recommendations_for_api

        valid_cities = get_valid_cities_from_df(df)
        cli_args = ["--city", req.city.strip(), "--price", req.price.strip()]
        inp = get_validated_input(args=cli_args, valid_cities=valid_cities)
        user_input = {"city": inp.city, "min_price": inp.min_price, "max_price": inp.max_price}

        results = recommend_restaurants(df, user_input)
        enriched = enrich_recommendations_for_api(results, df, city=user_input["city"])

        empty = len(enriched) == 0
        message = None
        if empty:
            message = (
                "No recommendations found. Try increasing your budget "
                "(e.g. Medium or High) or a different city/locality."
            )

        return RecommendResponse(
            ok=True,
            user_input=_to_serializable(user_input),
            recommendations=_to_serializable(enriched),
            empty=empty,
            message=message,
        )
    except ValueError as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": str(e)},
        )
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": f"Server error: {e}"},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
