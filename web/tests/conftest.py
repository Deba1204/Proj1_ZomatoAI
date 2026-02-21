"""Fixtures for web API tests: test DataFrame and dependency override."""

import sys
from pathlib import Path

import pandas as pd
import pytest

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


@pytest.fixture
def test_df():
    """Minimal DataFrame with columns required by phase2 and recommendation engine."""
    return pd.DataFrame({
        "name": ["Cafe A", "Restaurant B"],
        "city": ["btm", "btm"],
        "rate": [4.2, 4.0],
        "votes": [100, 50],
        "approx_cost(for two people)": [400, 800],
        "cuisines": ["North Indian", "South Indian"],
        "location": ["BTM", "BTM 2nd stage"],
        "address": ["123 Main St", "456 Cross Rd"],
    })


@pytest.fixture
def client(test_df):
    """FastAPI TestClient with get_df overridden to return test_df (no HuggingFace)."""
    from fastapi.testclient import TestClient
    from web.app import app, get_df

    def override_get_df():
        return test_df

    app.dependency_overrides[get_df] = override_get_df
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
