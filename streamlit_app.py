"""
Zomato AI — Streamlit deployment.

Same recommendation pipeline as the FastAPI/React stack: load dataset, validate city/price,
run Groq LLM recommendation, display results. Run locally or deploy on Streamlit Cloud.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Load .env (phase4) before any groq/recommendation imports
def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv(_ROOT / ".env", override=True)
        load_dotenv(_ROOT / "phase4" / ".env", override=True)
    except ImportError:
        pass
    import os
    if not os.environ.get("GROQ_API_KEY", "").strip() and (_ROOT / "phase4" / ".env").exists():
        try:
            with open(_ROOT / "phase4" / ".env", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        if k.strip() == "GROQ_API_KEY":
                            os.environ["GROQ_API_KEY"] = v.strip().strip('"').strip("'")
                            break
        except Exception:
            pass

_load_env()

import streamlit as st
import pandas as pd


@st.cache_data(ttl=3600)
def load_dataset():
    """Load and cache the cleaned Zomato dataset (HuggingFace)."""
    from phase1.loader import load_and_prepare
    return load_and_prepare(print_schema_output=False)


def get_cities(df: pd.DataFrame):
    from phase2.handler import get_valid_cities_from_df
    return get_valid_cities_from_df(df)


def run_recommendations(df: pd.DataFrame, city: str, price: str):
    """Validate input, run recommendation engine, return (user_input, results, error)."""
    from phase2.handler import get_validated_input
    from recommendation.engine import recommend_restaurants
    from display.formatter import enrich_recommendations_for_api

    valid_cities = get_cities(df)
    try:
        inp = get_validated_input(
            args=["--city", city.strip(), "--price", price.strip()],
            valid_cities=valid_cities,
        )
    except Exception as e:
        return None, None, str(e)

    user_input = {"city": inp.city, "min_price": inp.min_price, "max_price": inp.max_price}
    try:
        results = recommend_restaurants(df, user_input)
        enriched = enrich_recommendations_for_api(results, df, city=user_input["city"])
        return user_input, enriched, None
    except Exception as e:
        return user_input, None, str(e)


def main():
    st.set_page_config(page_title="Zomato AI", page_icon="🍽️", layout="centered")
    st.title("🍽️ Zomato AI")
    st.markdown("Restaurant recommendations by **city** and **budget** (powered by Groq LLM).")

    with st.spinner("Loading dataset..."):
        df = load_dataset()
    cities = get_cities(df)
    if not cities:
        st.error("No cities found in dataset. Check data load.")
        return

    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("City / Locality", options=cities, index=0, key="city")
    with col2:
        price = st.text_input(
            "Price",
            value="500",
            placeholder="e.g. 500, 500-1000, Low, Medium, High",
            key="price",
        )

    if st.button("Get recommendations", type="primary"):
        if not price.strip():
            st.warning("Please enter a price (e.g. 500 or Medium).")
            return
        with st.spinner("Finding recommendations..."):
            user_input, results, err = run_recommendations(df, city, price)
        if err:
            st.error(err)
            return
        if not results:
            st.info(
                "No recommendations found. Try increasing your budget "
                "(e.g. Medium or High) or a different city."
            )
            return
        # Build display table (native types for Streamlit display)
        def _val(x):
            if x is None: return "—"
            if hasattr(x, "item"): return x.item()
            return x

        rows = []
        for i, r in enumerate(results, 1):
            rows.append({
                "Rank": i,
                "Name": _val(r.get("name")) or "—",
                "Rating": _val(r.get("rating") or r.get("rate")) or "—",
                "Votes": _val(r.get("votes")) or "—",
                "Cost (for 2)": _val(r.get("cost_for_two")) or "—",
                "Cuisines": _val(r.get("cuisines")) or "—",
                "Locality": _val(r.get("locality")) or "—",
                "Address": _val(r.get("address")) or "—",
            })
        out = pd.DataFrame(rows)
        st.success(f"Found **{len(out)}** recommendations for **{city}** (budget: ₹{user_input['min_price']}–{user_input['max_price']}).")
        st.dataframe(out, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
