"""
Groq LLM client wrapper, prompt template, and JSON parsing.

Uses environment variable GROQ_API_KEY (never hardcoded).
Loads .env from project root and phase4/.env if python-dotenv is installed.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Load .env so GROQ_API_KEY from phase4/.env or project root .env is available
def _load_dotenv() -> None:
    root = Path(__file__).resolve().parent.parent
    # Try python-dotenv first
    try:
        from dotenv import load_dotenv
        load_dotenv(root / ".env", override=True)
        load_dotenv(root / "phase4" / ".env", override=True)
    except ImportError:
        pass
    # Fallback: if key still not set, read phase4/.env manually (e.g. if dotenv path was wrong)
    if not os.environ.get("GROQ_API_KEY", "").strip():
        _env_file = root / "phase4" / ".env"
        try:
            if _env_file.exists():
                with open(_env_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            if key.strip() == "GROQ_API_KEY":
                                os.environ["GROQ_API_KEY"] = value.strip().strip('"').strip("'")
                                break
        except Exception:
            pass

_load_dotenv()

# Optional import so tests can run without groq installed
try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

DEFAULT_MODEL = "llama-3.3-70b-versatile"
# Alternative: "mixtral-8x-7b-32768"


def get_api_key() -> str:
    """Return GROQ_API_KEY from environment. Raises if missing or empty."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        _load_dotenv()  # Retry load (e.g. .env may be available now when running tests)
        key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "GROQ_API_KEY is not set. Set it in your environment or phase4/.env file to use recommendations."
        )
    return key


def get_client() -> "Groq":
    """Return a Groq client using GROQ_API_KEY from environment."""
    if Groq is None:
        raise ImportError("Package 'groq' is not installed. Install with: pip install groq")
    return Groq(api_key=get_api_key())


def build_ranking_prompt(candidates: List[Dict[str, Any]], city: str) -> str:
    """
    Build the system + user prompt for LLM to rank candidates.

    LLM must only choose from the candidates list and return top 10 in JSON.
    """
    candidates_text = json.dumps(candidates, indent=2)
    system_prompt = (
        "You are a restaurant recommendation assistant. "
        "You will receive a list of restaurant candidates in JSON. "
        "Your task is to rank and return exactly the top 10 best options. "
        "You MUST only choose from the given list; do not add or invent restaurants. "
        "Respond with a single JSON object with key 'recommendations' containing an array of "
        "exactly 10 objects, each with at least 'name' and optionally 'reason' (short reason). "
        "Example: {\"recommendations\": [{\"name\": \"Restaurant A\", \"reason\": \"...\"}, ...]}"
    )
    user_prompt = (
        f"City/area: {city}\n\n"
        f"Candidates (choose top 10 from this list only):\n{candidates_text}\n\n"
        "Return the top 10 recommendations as JSON with key 'recommendations'."
    )
    return system_prompt, user_prompt


def call_groq_rank(
    candidates: List[Dict[str, Any]],
    city: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Call Groq API to rank candidates and return top 10. Returns raw response content (JSON string).
    """
    client = get_client()
    system_prompt, user_prompt = build_ranking_prompt(candidates, city)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    content = response.choices[0].message.content
    return content or "{}"


def parse_recommendations_json(raw: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response into list of recommendation dicts.
    Expects JSON like {"recommendations": [{"name": "...", "reason": "..."}, ...]}.
    Falls back to extracting JSON from markdown code blocks if present.
    """
    if not raw or not raw.strip():
        return []

    s = raw.strip()
    # Remove markdown code block if present
    code_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s)
    if code_match:
        s = code_match.group(1).strip()
    # Find first { ... } if there's extra text
    start = s.find("{")
    if start >= 0:
        depth = 0
        for i in range(start, len(s)):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    s = s[start : i + 1]
                    break
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        return []

    if isinstance(data, dict) and "recommendations" in data:
        recs = data["recommendations"]
        if isinstance(recs, list):
            return [r if isinstance(r, dict) else {"name": str(r)} for r in recs[:10]]
    if isinstance(data, list):
        return [r if isinstance(r, dict) else {"name": str(r)} for r in data[:10]]
    return []


def rank_with_groq(
    candidates: List[Dict[str, Any]],
    city: str,
    model: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Call Groq to rank candidates and return parsed top 10 list of dicts.
    """
    model = model or DEFAULT_MODEL
    raw = call_groq_rank(candidates, city, model=model)
    return parse_recommendations_json(raw)
