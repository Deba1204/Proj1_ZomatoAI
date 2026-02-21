"""Load phase4/.env before tests so GROQ_API_KEY is set for LLM tests."""

import os
from pathlib import Path


def pytest_configure(config):
    """Load .env from phase4/ at session start so GROQ_API_KEY is available."""
    phase4_dir = Path(__file__).resolve().parent.parent
    env_file = phase4_dir / ".env"
    # Try python-dotenv
    try:
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(dotenv_path=str(env_file.resolve()), override=True)
    except ImportError:
        pass
    # Fallback: read GROQ_API_KEY from file manually
    if not os.environ.get("GROQ_API_KEY", "").strip() and env_file.exists():
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        if key.strip() == "GROQ_API_KEY":
                            os.environ["GROQ_API_KEY"] = value.strip().strip('"').strip("'")
                            break
        except Exception:
            pass
